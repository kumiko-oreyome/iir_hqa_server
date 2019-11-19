from dataloader.dureader import  DureaderRawExample
from common.util import RecordGrouper,group_dict_list
from qa.judger import TopKJudger
from qa.ranker import RankerFactory
from qa.reader import ReaderFactory
from common.util import get_default_device
import httpx


class MockMRCModel():
    def __init__(self):
        pass
    def get_answer_list(self,mrc_input,k=3):
        x = DureaderRawExample(mrc_input)
        l = x.flatten(['question'],['url','title'])
        l = l [0:k]
        ret = []
        for x in l:
            if len( x['passage'])>10:
               answer = x['passage'][10:20]
            else:
               answer  = x['passage'][0:10]
            ret.append({'paragraph':x['passage'],'answer':answer,'title':x['title'],'url':x['url']})
        return ret


class RankerReaderModel():
    def __init__(self,ranker,reader):
        self.ranker = ranker
        self.reader = reader

    def get_answer_list(self,mrc_input,k=3):
        mrc_input['id'] = 0
        x = DureaderRawExample(mrc_input)
        records = x.flatten(['question','id'],['url','title'])
        doc_num  = len(mrc_input['documents'])
        ranked_records  = self.ranker.evaluate_on_records(records,64)
        group = RecordGrouper(ranked_records)
        ranked_records = group.group_sort('id','rank_score')[0]
        ranked_records = ranked_records[0:doc_num]
        reader_results = self.reader.evaluate_on_records(ranked_records,64)
        reader_results = group_dict_list(reader_results,'id')
        ret_list= TopKJudger(k=k).judge(reader_results)[0]
        ret = []
        for x in ret_list:
            ret.append({'paragraph':x['passage'],'answer':x['span'],'title':x['title'],'url':x['url']})
        return ret


def multi_doc_model_factory(config):
    if config['model_type'] == 'mock':
        return MockMRCModel()
    elif config['model_type'] == 'pipeline':
        if 'device' in config:
            import torch
            device = config['device']
            if device == 'cpu':
                device = torch.device('cpu')
            else:
                device =  get_default_device()
        ranker = RankerFactory.from_config_path(config['ranker_config_path'])
        reader = ReaderFactory.from_config_path(config['reader_config_path'])
        try:
            ranker.model = ranker.model.to(device)
        except:
            pass
        try:
            reader.model = reader.model.to(device)
        except:
            pass
        return RankerReaderModel(ranker,reader)



class TestMrcApp():
    def __init__(self,config):
        from mrc_server import create_app
        self.app = create_app(config)
    def multi_mrc(self,mrc_input,answer_num=3,algo_version=0):
        with self.app.test_client() as c:
            rv = c.post('/qa', json={'mrc_input':mrc_input,'answer_num':answer_num,'algo_version':algo_version})
        return rv.get_json()


class RedirectMrcModel():
    def __init__(self,server_url):
        self.server_url = server_url
    def multi_mrc(self,mrc_input,answer_num=3,algo_version=0):
        try:
            r = httpx.post(self.server_url,json={'mrc_input':mrc_input,'answer_num':answer_num,'algo_version':algo_version},timeout=60)
        except Exception as e:
            import traceback
            traceback.print_exc()
            print('some error occur while redirect to mrc server %s'%(self.server_url))
            return {'result':'failed','message':'some error occur while redirect'}
        print(r)
        return r.json()