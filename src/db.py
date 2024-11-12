from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
# from src.app import app
# from flask_login import UserMixin

db = SQLAlchemy() #create db


class User(db.Model): #db table for users should be modified in future
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60),nullable=False)
    surname = db.Column(db.String(60),nullable=False)
    email = db.Column(db.String(60),unique=True,nullable=False)
    password = db.Column(db.Text())
    registred_at = db.Column(db.DateTime,nullable=False,default=datetime.now())
    updated_at = db.Column(db.DateTime,onupdate=datetime.now(),nullable=True)
    def __repr__(self):
        return f"User>>> {self.name}"
class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(300), nullable=False)
    photo_file = db.Column(db.String(100), nullable=True)

    def __init__(self, location, description, photo_file = None):
        self.location = location
        self.description = description
        self.photo_file = photo_file

