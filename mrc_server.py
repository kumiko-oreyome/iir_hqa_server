from flask import Flask
from qa_mrc.dataloader.dureader import  DureaderRawExample
#paragraphs.append({'paragraph':paragraph,'answer':paragraph[0:2],'title':'這是標題[%d]拉哈哈'%(i+1),'url':'https://www.google.com.tw'})





class MockMRCModel():
    def __init__(self):
        pass
    def get_answer_list(self,mrc_input,k=3):
        x = DureaderRawExample(mrc_input)
        l = x.flatten(['question'],['url','title'])
        l = l [0:k]
        for x in l:
            if len( x['passage'])>10:
                x['answer'] = x['passage'][10:20]
            else:
                x['answer'] = x['passage'][0:10]
        return l


def create_app(config):
    app = Flask(__name__)
    #app.config['DEBUG'] = True 
    app.config.from_mapping(
        SECRET_KEY='key'
    )
    for k,v in config.items():
        app.config[k] = v
    import api_view
    import asyncio
    loop = asyncio.get_event_loop()
    app.register_blueprint(api_view.create_bp(app))



def multi_doc_model_factory(config):
    if config['model_type'] == 'mock':
        return MockMRCModel()