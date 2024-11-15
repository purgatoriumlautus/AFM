import os
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask import Flask
from src.routes import register_routes
from flask_sqlalchemy import SQLAlchemy
from src.db import db
from src.models import User
from flask_migrate import Migrate


def create_app():
    app = Flask(__name__, template_folder='templates')
    app.config['UPLOAD_FOLDER'] = 'src/static'
    
    #set up the db
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("FLASK_SQLALCHEMY_DATABASE_URI")
    db.init_app(app)
    migrate = Migrate(app,db)
    
    bcrypt = Bcrypt(app)

    # should be changed to something more secure
    app.secret_key = "secret"

    # login manager
    login_manager = LoginManager()
    login_manager.init_app(app)

    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
 

    register_routes(app, db, bcrypt)
    
    return app


# app.register_blueprint(user)