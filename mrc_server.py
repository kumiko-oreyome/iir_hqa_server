from flask import Flask,request,jsonify
from qa_mrc.dataloader.dureader import  DureaderRawExample
from qa_mrc.common.util import get_default_device,RecordGrouper,group_dict_list
from qa_mrc.qa.ranker import RankerFactory
from qa_mrc.qa.reader import ReaderFactory
from qa_mrc.qa.judger import TopKJudger
from util import RequestMultiMRC,check_input_format
#paragraphs.append({'paragraph':paragraph,'answer':paragraph[0:2],'title':'這是標題[%d]拉哈哈'%(i+1),'url':'https://www.google.com.tw'})





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
    


def create_app(config):
    print('create app')
    app = Flask(__name__)
    #app.config['DEBUG'] = True 
    app.config.from_mapping(
        SECRET_KEY='key'
    )
    for k,v in config.items():
        app.config[k] = v
    print('create model')
    model = multi_doc_model_factory(config)
    @app.route('/qa',methods=['POST'])
    def qa_by_multi_mrc():
        req = RequestMultiMRC(request.json)
        if not check_input_format(req.mrc_input,"multi_mrc"):
            return jsonify({'result':'failed','message':'invalid input format'})
        answer_list = model.get_answer_list(req.mrc_input,req.answer_num)
        return jsonify({'result':'success','message':'success','answers':answer_list})
    return app


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


if __name__ == '__main__':
    config = {'model_type':'mock'}
    app = create_app(config )
    app.run(debug=False)