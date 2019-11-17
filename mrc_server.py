from flask import Flask,request,jsonify
from qa_mrc.dataloader.dureader import  DureaderRawExample
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


def create_app(config):
    app = Flask(__name__)
    #app.config['DEBUG'] = True 
    app.config.from_mapping(
        SECRET_KEY='key'
    )
    for k,v in config.items():
        app.config[k] = v
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


if __name__ == '__main__':
    config = {'model_type':'mock'}
    app = create_app(config )
    app.run(debug=False)