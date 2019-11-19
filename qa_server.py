from flask import Flask

def create_app(config):
    app = Flask(__name__)
    #app.config['DEBUG'] = True 
    app.config.from_mapping(
        SECRET_KEY='key'
    )
    import api_view
    import asyncio
    loop = asyncio.get_event_loop()
    app.register_blueprint(api_view.create_bp(app,loop,config))
    return app




if __name__ == '__main__':
    import  qa_server_config 
    app = create_app(qa_server_config.MODEL_CONFIG)
    app.run(debug=False)
