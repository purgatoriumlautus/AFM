from flask import Flask
import os
from src.userAPI import user
from src.db import db
from flask_jwt_extended import JWTManager


def create_app(test_config=None): #test_config for the development config
    app = Flask(__name__,
                instance_relative_config=True)
    

    if test_config is None: #if test_config is none then set this config 
        app.config.from_mapping( #set config from this mappings.
            SECRET_KEY= os.environ.get("SECRET_KEY"), #get the environmental value of secret key
            SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DB_URI'), #get the environmental value of the db's uri
            SQLALCHEMY_TRACK_MODIFICATIONS=False, #For db to not track the modifications in it
            JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') #get the environmental value of jwt token(used for authentication)
        )

    else:
        app.config.from_mapping(test_config)
    

    db.app = app #pass the app to the db
    db.init_app(app) #link the app to db

    JWTManager(app) #set the jwt manager for the app (for authentication)

    app.register_blueprint(user) #add a user blueprint


    # add individual namespaces
    return app

