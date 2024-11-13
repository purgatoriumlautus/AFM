class Task:
    def __init__(self, id, description, priority):
        self.id = id
        self.description = description
        self.priority = priority
        self.done = False
        self.responders_id = []

    def mark_done(self):
        self.done = True
    def add_responder(self, responder_id):
        self.responders_id.append(responder_id)
    def remove_responder(self, responder_id):
        self.responders_id.remove(responder_id)
    def update_priority(self, priority):
        self.priority = priority
    def update_description(self, description):
        self.description = description
