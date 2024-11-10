from flask_login import UserMixin
class User():
    def __init__(self, name, surname, email, password, phone, location = None):
        self.name = name
        self.surname = surname
        self.email = email
        self.password = password
        self.phone = phone
        self.location = None
    def update_name(self, name):
        self.name = name
    def update_surname(self, surname):
        self.surname = surname
    def update_email(self, email):
        self.email = email
    def update_password(self, password):
        # has to be hased obviously
        self.password = password
    def update_phone(self, phone):
        self.phone = phone
    def update_location(self, location):
        self.location = location
