from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail, Message
from flask_socketio import SocketIO

socketio = SocketIO(cors_allowed_origins="*")
bcrypt = Bcrypt()
login_manager = LoginManager()
mail = Mail()


