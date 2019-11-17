from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for,Markup,jsonify
)
from util import  RequestQA


def create_bp(app):
    bp = Blueprint('api', __name__, url_prefix='/api')
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
        return jsonify(response)
    return bp
