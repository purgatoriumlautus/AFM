from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60),nullable=False)
    surname = db.Column(db.String(60),nullable=False)
    email = db.Column(db.String(60),unique=True,nullable=False)
    password = db.Column(db.Text())
    registred_at = db.Column(db.DateTime,nullable=False,default=datetime.now())
    updated_at = db.Column(db.DateTime,onupdate=datetime.now(),nullable=True)


    def __repr__(self):
        return f"User>>> {self.name}"
    

