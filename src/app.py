import os
from flask_migrate import Migrate
from flask import Flask
# from src.routes import register_routes
from src.db import db
from src.models import User
from flask_migrate import Migrate
from src.extensions import  bcrypt,login_manager,mail
from src.routes.auth import auth
from src.routes.main import main
from src.routes.reports import report
from src.routes.tasks import task
from src.routes.admin import admin
from src.routes.superadmin import superadmin
from flask import current_app
from flask_apscheduler import APScheduler
from datetime import datetime, timedelta, timezone


# Create the Flask app and initialize the scheduler
def create_app():
    app = Flask(__name__, template_folder='templates')
    app.config['UPLOAD_FOLDER'] = 'src/static'

    # Set up the database
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('FLASK_SQLALCHEMY_DATABASE_URI',
                                                      'postgresql://user:secret@localhost:5432/postgres')

    app.config['SCHEDULER_API_ENABLED'] = True
    db.init_app(app)

    migrate = Migrate(app, db)

    bcrypt.init_app(app)

    # Application secret key (should be more secure in production)
    app.secret_key = "secret"

    # Email setup for Flask-Mail
    app.config['MAIL_SERVER'] = "smtp.gmail.com"
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False
    app.config['MAIL_USERNAME'] = 'afm.team.contact@gmail.com'
    app.config['MAIL_PASSWORD'] = 'vqmt apss felo iwon'
    app.config['MAIL_DEFAULT_SENDER'] = 'AFM Team, afm.team.contact@gmail.com'
    mail.init_app(app)
    login_manager.init_app(app)

    app.register_blueprint(auth)
    app.register_blueprint(main)
    app.register_blueprint(report)
    app.register_blueprint(task)
    app.register_blueprint(admin)
    app.register_blueprint(superadmin)


    scheduler = APScheduler()
    scheduler.init_app(app)
    @scheduler.task('interval', id='delete_unverified_users', hours=24, misfire_grace_time=900)
    def delete_unverified_users():
        with app.app_context():
            expiration_time = datetime.now(timezone.utc) - timedelta(days=3)
            # Efficiently delete users directly in the database
            try:
                User.query.filter(
                    User.email_confirmed == False,
                    User.created_at < expiration_time
                ).delete(synchronize_session=False)  # Skip in-memory synchronization for speed.

                db.session.commit()
            except Exception as e:
                db.session.rollback()

    # Start the scheduler
    scheduler.start()
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app