from flask_login import UserMixin
from src.app import db


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}

    uid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)

    def __repr__(self):
        return f'<User {self.username}>'

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
