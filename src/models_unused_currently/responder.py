from .user import User
#CLASS RESPONDER EXTENDS CLASS USER (TAKES NAME, ORGANISATION ID, PHONE, STATUS)
# basically they have same attributes and methods as User class with additional ones
class Responder(User):
    def __init__(self, responder_id, name, organisation_id, phone, status):
        self.responder_id = responder_id
        self.name = name
        self.organisation_id = organisation_id
        self.phone = phone
        self.status = status
        self.assigned_tasks = []
    def update_organisation_id(self, organisation_id):
        self.organisation_id = organisation_id
    def update_status(self, status):
        self.status = status
    def assign_task(self, task_id):
        self.assigned_tasks.append(task_id)