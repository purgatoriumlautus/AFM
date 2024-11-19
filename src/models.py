from flask_login import UserMixin
from src.db import db  



class User(db.Model, UserMixin):
    __tablename__ = 'users'

    uid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)

    def __repr__(self):
        return f'<User {self.username}>'
    def get_id(self):
        return self.uid


class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(300), nullable=False)
    photo_file = db.Column(db.String(100), nullable=True)
    def __init__(self, location, description, photo_file = None):
        self.location = location
        self.description = description
        self.photo_file = photo_file
    @staticmethod
    def all_reports():
        return Report.query.all()

    # def __init__(self, name, surname, email, password, phone, location = None):
    #     self.name = name
    #     self.surname = surname
    #     self.email = email
    #     self.password = password
    #     self.phone = phone
    #     self.location = None
    # def get_id(self):
    #     return self.uid
    # def update_name(self, name):
    #     self.name = name
    # def update_surname(self, surname):
    #     self.surname = surname
    # def update_email(self, email):
    #     self.email = email
    # def update_password(self, password):
    #     # has to be hased obviously
    #     self.password = password
    # def update_phone(self, phone):
    #     self.phone = phone
    # def update_location(self, location):
    #     self.location = location

