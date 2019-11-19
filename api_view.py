from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for,Markup,jsonify
)
from util import  RequestQA
from multi_mrc import TestMrcApp,RedirectMrcModel
from document_retrieval import WebRetriever,GoogleSearchRetriever,FakeRetriever



def wrap_response(json):
    if 'result' not in json and 'answers' in json:
        json['result'] = 'success'
    return json
    




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
    retriever  = doc_retriever_factory(config['document_retrieval'])
    multi_mrc_model =  multi_mrc_factory(config['multi_mrc'])



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
        response.update({'question':req.question,'algo_version':req.algo_version})
        return jsonify(wrap_response(response))

    return bp
