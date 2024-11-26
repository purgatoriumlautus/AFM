from flask_login import UserMixin
from src.db import db
from datetime import datetime


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    uid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    last_location = db.Column(db.String(100), nullable=True)
    is_owner = db.Column(db.Boolean, default=False)

    # 1 user : 1 report
    report = db.relationship('Report', back_populates='creator', uselist=False)


    # These are one-to-one relationships but optional
    agent = db.relationship('Agent', back_populates='user', uselist=False)
    manager = db.relationship('Manager', back_populates='user', uselist=False)
    organisation_id = db.Column(db.Integer, db.ForeignKey('organizations.id'))



    def __repr__(self):
        return f'<User {self.username}>'

    def get_id(self):
        return self.uid

    @staticmethod
    def all_users():
        return User.query.all()



class Agent(db.Model):
    __tablename__ = 'agents'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.uid'), nullable=False)
    position = db.Column(db.String(100), nullable=False, default="Agent")

    user = db.relationship('User', back_populates='agent')

    def __repr__(self):
        return f"<Agent {self.id}, Position: {self.position}>"



class Manager(db.Model):
    __tablename__ = 'managers'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.uid'), nullable=False)
    position = db.Column(db.String(100), nullable=False, default="Manager")

    user = db.relationship('User', back_populates='manager')    # One-to-One relationship


    def __repr__(self):
        return f"<Manager {self.id}, Position: {self.position}>"



class Report(db.Model):
    __tablename__ = 'reports'
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(300), nullable=False)
    photo_file = db.Column(db.String(100), nullable=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.uid'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_approved = db.Column(db.Boolean, default=False, nullable=False)
    approver_id = db.Column(db.Integer, db.ForeignKey('managers.id'), nullable=True)
    creator = db.relationship('User', back_populates='report')
    approver = db.relationship('Manager', backref='approved_reports')
    def __init__(self, location, description, photo_file=None, creator_id=None, task_id=None):
        self.location = location
        self.description = description
        self.photo_file = photo_file
        self.creator_id = creator_id
        self.task_id = task_id

    @staticmethod
    def all_reports():
        return Report.query.all()

class Organisation(db.Model):
    __tablename__ = 'organizations'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    token = db.Column(db.String(100), unique=True, nullable=True)

    # Relationship with users
    users = db.relationship('User', backref='organization')

db.UniqueConstraint('organization_id', 'is_owner', name='unique_owner_organization')


