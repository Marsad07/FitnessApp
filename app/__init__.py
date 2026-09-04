from flask import Flask

def create_app():
    app = Flask(__name__)
    from .routes import bp1
    app.register_blueprint(bp1)
    return app

