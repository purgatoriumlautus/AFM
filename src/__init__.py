from flask import Flask
import os
from src.user import user
from src.db import db
from flask_jwt_extended import JWTManager


def create_app(test_config=None):
    app = Flask(__name__,
                instance_relative_config=True)
    
    # need to extend this class for custom objects, so that they can be jsonified
    if test_config is None:
        app.config.from_mapping(
            SECRET_KEY= os.environ.get("SECRET_KEY"),
            SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DB_URI'),
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
            JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
        )

    else:
        app.config.from_mapping(test_config)
    

    db.app = app
    db.init_app(app)

    JWTManager(app)

    app.register_blueprint(user)


    # add individual namespaces
    return app

