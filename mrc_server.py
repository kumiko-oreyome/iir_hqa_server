from flask import Flask

#paragraphs.append({'paragraph':paragraph,'answer':paragraph[0:2],'title':'這是標題[%d]拉哈哈'%(i+1),'url':'https://www.google.com.tw'})


class MockMRCModel():
    def __init__(self):
        pass
    def get_answer_list(self,mrc_input,k=3):
        pass


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