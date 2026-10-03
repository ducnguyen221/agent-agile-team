from flask import Flask

from . import config
from .routes import bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(config)
    app.register_blueprint(bp)
    return app
