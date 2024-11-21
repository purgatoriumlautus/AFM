import os
from flask_migrate import Migrate
from flask import Flask
# from src.routes import register_routes
from src.db import db
from src.models import User
from flask_migrate import Migrate
from src.extensions import  bcrypt,login_manager
from src.routes.auth import auth
from src.routes.main import main
from src.routes.reports import report
from src.routes.tasks import task
from src.routes.admin import admin


def create_app():
    app = Flask(__name__, template_folder='templates')
    app.config['UPLOAD_FOLDER'] = 'src/static'
    #set up the db
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("FLASK_SQLALCHEMY_DATABASE_URI")
    db.init_app(app)
    migrate = Migrate(app,db)
    

    bcrypt.init_app(app)

    # should be changed to something more secure
    app.secret_key = "secret"

    # login manager
    
    login_manager.init_app(app)


    app.register_blueprint(auth)
    app.register_blueprint(main)
    app.register_blueprint(report)
    app.register_blueprint(task)
    app.register_blueprint(admin)
    
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
 

    # register_routes(app, db, bcrypt)
    
    return app


# app.register_blueprint(user)