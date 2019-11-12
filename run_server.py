from flask import Flask

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
    return app




if __name__ == '__main__':
    CONFIG = {}
    app = create_app(CONFIG )
    app.run(debug=True)
