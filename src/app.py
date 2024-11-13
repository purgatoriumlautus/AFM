from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
# from src.routes import register_routes
# app.register_blueprint(user)
db = SQLAlchemy()

def create_app():
    app = Flask(__name__, template_folder='templates')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.secret_key = "secret"
    # initialize db
    db.init_app(app)

    migrate = Migrate(app, db)

    # login manager
    login_manager = LoginManager()
    login_manager.init_app(app)

    from src.models import User


    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)

    bcrypt = Bcrypt(app)

    from src.routes import register_routes
    register_routes(app, db, bcrypt)

    return app




