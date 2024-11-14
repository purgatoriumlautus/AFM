import os
from flask import Flask
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from src.db import db  # Import db from db.py

def create_app():
    app = Flask(__name__, template_folder='templates')

    # Construct the absolute path for the database file
    instance_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'instance')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(instance_path, 'database.db')

    # should be changed to something more secure
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
        return User.query.get(int(user_id))

    # add bcrypt to the app (used for hashing passwords)
    bcrypt = Bcrypt(app)

    from src.routes import register_routes
    register_routes(app, db, bcrypt)

    return app