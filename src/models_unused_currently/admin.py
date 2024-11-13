from .user import User
class Admin(User):
    def __init__(self, admin_id, name, email, phone):
        self.admin_id = admin_id
        self.name = name
        self.email = email
        self.phone = phone
    def update_phone(self, phone):
        self.phone = phone
    def update_name(self, name):
        self.name = name
    def update_email(self, email):
        self.email = email
    def update_password(self, password):
        self.password = password
