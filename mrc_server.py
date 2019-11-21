from flask import Flask,request,jsonify
from util import RequestMultiMRC,check_input_format
from multi_mrc import MockMRCModel,RankerReaderModel,multi_doc_model_factory
#paragraphs.append({'paragraph':paragraph,'answer':paragraph[0:2],'title':'這是標題[%d]拉哈哈'%(i+1),'url':'https://www.google.com.tw'})




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
        print('qa_by_multi_mrc')
        if request.json is None:
            return jsonify({'result':'failed','message':'request is not json'})
        req = RequestMultiMRC(request.json)
        if not check_input_format(req.mrc_input,"multi_mrc"):
            return jsonify({'result':'failed','message':'invalid input format'})
        answer_list = model.get_answer_list(req.mrc_input,req.answer_num)
        return jsonify({'result':'success','message':'mrc success','answers':answer_list})
    return app



if __name__ == '__main__':
    import  mrc_server_config 
    app = create_app( mrc_server_config.MODEL_CONFIG)
    app.run(debug=False, port=mrc_server_config.PORT,threaded=True)