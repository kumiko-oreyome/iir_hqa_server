from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for,Markup,jsonify
)
from util import  RequestQA,check_input_format
from common.util import jsonl_reader
from multi_mrc import TestMrcApp,RedirectMrcModel
from document_retrieval import WebRetriever,GoogleSearchRetriever,FakeRetriever,CMKBElasticSearchRetriever
from preprocessing import   SimpleParagraphTransform
from dataloader.dureader import  DureaderRawExample
from datautil.cmkb import  CMKBElasticDB

def wrap_response(json):
    if 'result' not in json and 'answers' in json:
        json['result'] = 'success'
    return json
    
def load_keyword_dict(path):
    return set([l.rstrip() for l in open(path,'r',encoding='utf-8')])




def create_bp(app,event_loop,config):
    def doc_retriever_factory(retriever_config):
        name2class = {'GoogleSearchRetriever': GoogleSearchRetriever,'FakeRetriever':FakeRetriever}
        _cls = name2class[retriever_config['class']]
        if issubclass(_cls,WebRetriever):
            print('event loop %s'%(str(event_loop)))
            return _cls(event_loop=event_loop,**retriever_config['kwargs'])

        return _cls(**retriever_config['kwargs'])
    def multi_mrc_factory(model_config):
        name2class = {'TestMrcApp':TestMrcApp,'RedirectMrcModel':RedirectMrcModel}
        _cls = name2class[model_config['class']]
        return _cls(**model_config['kwargs'])

    bp = Blueprint('api', __name__, url_prefix='/api')
    print('initialze server')
    retriever  = doc_retriever_factory(config['document_retrieval'])
    multi_mrc_model =  multi_mrc_factory(config['multi_mrc'])
    es_db = CMKBElasticDB(**config["el_config"])
    import jieba  
    jieba.analyse.set_stop_words('./data/stopwords.txt')
    keyword_dict = load_keyword_dict(config['kw_dict_path'])
    cmkb_elk_retriever =   CMKBElasticSearchRetriever(es_db,5,keyword_dict)
    print('complete initialze')



    @bp.route('/fake_qa',methods=['POST'])
    def fake_qa():
        req = RequestQA(request.json)
        paragraphs = []
        response = {'question':req.question,'algo_version':req.algo_version}
        fake_paragraphs = ['你怎麼不問神奇海螺','發大財','國家機器動得很勤勞']
        for i in range(req.answer_num):
            if i >= 3:
                paragraph = '段落%d:\n 你要的還真多,貪心的人,我沒梗了'%(i+1)
            else:
                paragraph = fake_paragraphs[i]
            paragraphs.append({'paragraph':paragraph,'answer':paragraph[0:2],'title':'這是標題[%d]拉哈哈'%(i+1),'url':'https://www.google.com.tw'})
        response['answers'] = paragraphs
        return jsonify(wrap_response(response))

    
    @bp.route('/webqa',methods=['POST'])
    def qa_by_websearch():
        print('qa_by_websearch')
        req = RequestQA(request.json)
        mrc_input = retriever.retrieve_candidates(req.question)
        response = multi_mrc_model.multi_mrc(mrc_input)
        if response['result']!='success':
            return  jsonify(response)
        for answer in response['answers']:
            start_pos = answer['paragraph'].find(answer['answer'] )
            answer['answer_pos'] = [start_pos,start_pos+len(answer['answer'])-1]
        response.update({'question':req.question,'algo_version':req.algo_version})
        return jsonify(wrap_response(response))



    @bp.route('/kbqa',methods=['POST'])
    def qa_by_cmkb():
        print('qa_by_cmkb')
        req = RequestQA(request.json)
        mrc_input = cmkb_elk_retriever.retrieve_candidates(req.question)
        response = multi_mrc_model.multi_mrc(mrc_input)
        print(list(response.keys()))
        if response['result']!='success':
            return  jsonify(response)
        for answer in response['answers']:
            start_pos = answer['paragraph'].find(answer['answer'] )
            answer['answer_pos'] = [start_pos,start_pos+len(answer['answer'])-1]
        response.update({'question':req.question,'algo_version':req.algo_version})
        return jsonify(wrap_response(response))


    @bp.route('/webqa_fast',methods=['POST'])
    def fast_qa_by_cmkb():
        from qa.para_select import WordMatchSelector
        import random
        if request.json is None:
            return jsonify({'result':'failed','message':'request is not json'})
        req = RequestQA(request.json)
        res = cmkb_elk_retriever.search_elk(req.question)[0:2]
        print('retrieve %d docs'%(len(res)))
        if len(res) == 0:
            keyword = '高血壓'
            if '糖尿病' in req.question:
                keyword = '糖尿病'
            target_sample = None
            for sample in jsonl_reader('./data/docs/fake_db.jsonl'):
                if keyword in sample['question']:
                    target_sample = sample
                    break
            assert target_sample is not None
            SimpleParagraphTransform().transform(target_sample)
            x = DureaderRawExample(target_sample)
            records = x.flatten(['question','qid'],['url','title'])
            results = WordMatchSelector(k=1).paragraph_selection(records)
            results = random.sample(results,k=2)      
        else:   
            records = []
            for i,x in enumerate(res):
                q = 'q:%d'%(i)
                for j,p in enumerate(x['paragraphs']):
                    obj = {'qid':i,'doc_id':i,'question':q,'passage':p,'url':x['url'],'title':x['title']}
                    records.append(obj)
            k = 1 if len(res)>1 else 2
            results = WordMatchSelector(k=k).paragraph_selection(records)
            results = random.sample(results,k=2) 
        response  = {'question':req.question,'algo_version':req.algo_version,'answers':[]}
        for x in results:
            response['answers'].append({'paragraph':x['passage'],'answer':'','answer_pos':[0,-1],'title':x['title'],'url':x['url']})
        return jsonify(wrap_response(response))

    return bp
