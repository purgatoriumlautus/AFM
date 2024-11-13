from .user import User
class Manager(User):
    def __init__(self, manager_id, name, organisation_id, phone):
        self.manager_id = manager_id
        self.name = name
        self.organisation_id = organisation_id
        self.phone = phone
        self.managed_tasks = []

        #Managers have organisations maybe?
    def update_organisation_id(self, organisation_id):
        self.organisation_id = organisation_id
    def create_task(self, task_id, description, priority):
        self.managed_tasks.append(task_id)