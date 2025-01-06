from flask_login import UserMixin
from src.db import db
from datetime import datetime
import os
from sqlalchemy import Index

sup_email = os.getenv("ADMIN_EMAIL")


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    uid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    home_address = db.Column(db.String(100), nullable=True)
    is_owner = db.Column(db.Boolean, default=False)
    is_banned = db.Column(db.Boolean, default=False)
    email_confirmed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    organisation_id = db.Column(
        db.Integer,
        db.ForeignKey('organisations.id', name='fk_user_organisation_id', ondelete='SET NULL', use_alter = True),
    )

    # Relationships
    report = db.relationship('Report', back_populates='creator', uselist=False)
    agent = db.relationship('Agent', back_populates='user', uselist=False)
    manager = db.relationship('Manager', back_populates='user', uselist=False)
    organisation = db.relationship(
        'Organisation',
        back_populates='users',
        foreign_keys=[organisation_id]  # Clarifies the foreign key for this relationship
    )

    __table_args__ = (
        Index(
            'unique_owner_organisation',  # Name of the index
            'organisation_id',
            unique=True,
            postgresql_where=db.text("is_owner = TRUE"),  # Apply the condition here
        ),
    )

    def __init__(self, username=None, password=None, email=None, is_owner=False, organisation_id=None,
                 email_confirmed=False, created_at=None, is_superadmin=False):
        self.username = username
        self.password = password
        self.email = email
        self.is_owner = is_owner
        self.organisation_id = organisation_id
        self.email_confirmed = email_confirmed
        self.created_at = created_at
        self.is_superadmin = is_superadmin

    def __repr__(self):
        return f'<User {self.username}>'

    def get_id(self):
        return self.uid

    @staticmethod
    def all_users():
        return User.query.all()

    def is_super_admin(self):
        return self.email == sup_email


agent_task = db.Table(
    'agent_task',
    db.Column('agent_id', db.Integer, db.ForeignKey('agents.id'), primary_key=True),
    db.Column('task_id', db.Integer, db.ForeignKey('tasks.id'), primary_key=True),
    db.Column('assigned_at', db.DateTime, default=datetime.utcnow)  # Track assignment time
)


class Agent(db.Model):
    __tablename__ = 'agents'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.uid'), nullable=False)
    position = db.Column(db.String(100), nullable=False, default="Agent")

    user = db.relationship('User', back_populates='agent')
    tasks = db.relationship('Task', secondary=agent_task, back_populates='agents')

    def __repr__(self):
        return f"<Agent {self.id}, Position: {self.position}>"


class Manager(db.Model):
    __tablename__ = 'managers'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.uid'), nullable=False)
    position = db.Column(db.String(100), nullable=False, default="Manager")

    user = db.relationship('User', back_populates='manager')

    def __repr__(self):
        return f"<Manager {self.id}, Position: {self.position}>"

task_report = db.Table(
    'task_report',
    db.Column('task_id', db.Integer, db.ForeignKey('tasks.id'), primary_key=True),
    db.Column('report_id', db.Integer, db.ForeignKey('reports.id'), primary_key=True)
)


class Report(db.Model):
    __tablename__ = 'reports'
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(300), nullable=False)
    photo_file = db.Column(db.String(100), nullable=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.uid'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    approver_id = db.Column(db.Integer, db.ForeignKey('managers.id', ondelete="SET NULL"), nullable=True)
    average_score = db.Column(db.Float, default=0.0, nullable=False)
    status = db.Column(db.String(50), default="", nullable=False)

    creator = db.relationship('User', back_populates='report')
    approver = db.relationship('Manager', backref='approved_reports')
    tasks = db.relationship('Task', secondary='task_report', back_populates='reports')
    def __init__(self, location, description, photo_file=None, creator_id=None, approver_id=None, is_approved=False,
                 avarage_score=None, score_count=None, status = ""):
        self.location = location
        self.description = description
        self.photo_file = photo_file
        self.creator_id = creator_id
        self.is_approved = is_approved
        self.average_score = avarage_score
        self.score_count = score_count
        self.status = status

    @staticmethod
    def all_reports():
        return Report.query.all()

    def add_score(self, user_id, score_value):
        existing_score = Score.query.filter_by(report_id=self.id, user_id=user_id).first()
        if existing_score:
            existing_score.score = score_value
            db.session.commit()
        else:
            new_score = Score(report_id=self.id, user_id=user_id, score=score_value)
            db.session.add(new_score)
            db.session.commit()
        self.recalculate_average_score()

    def recalculate_average_score(self):
        scores = [score.score for score in self.scores]
        if not scores:
            self.average_score = 0
        else:
            self.average_score = sum(scores) / len(scores)
        db.session.commit()

    def get_urgency(self):
        if self.average_score <= 30:
            return "Low Urgency"
        elif self.average_score <= 60:
            return "Medium Urgency"
        else:
            return "High Urgency"


class Score(db.Model):
    __tablename__ = 'scores'
    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, db.ForeignKey('reports.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.uid'), nullable=False)
    score = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    report = db.relationship('Report', backref=db.backref('scores'))
    user = db.relationship('User', backref=db.backref('scores'))
    __table_args__ = (db.UniqueConstraint('report_id', 'user_id', name='unique_user_report_score'),)

    def __init__(self, report_id, user_id, score):
        self.report_id = report_id
        self.user_id = user_id
        self.score = score

class Organisation(db.Model):
    __tablename__ = 'organisations'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    token = db.Column(db.String(100), unique=True, nullable=True)  # Link token for invites
    owner_id = db.Column(db.Integer, nullable=True)  # Soft reference to owner ID (not an FK)

    # Relationships
    users = db.relationship(
        'User',
        back_populates='organisation',
        foreign_keys='User.organisation_id',
        lazy='dynamic'
    )

    __table_args__ = (
        db.UniqueConstraint('id', name='unique_organisation_id'),
    )

    def __repr__(self):
        return f'<Organisation {self.name}>'


class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(300), nullable=True)  # Add description column
    creator_id = db.Column(db.Integer, db.ForeignKey('managers.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default="OPEN", nullable=False)

    creator = db.relationship('Manager', backref=db.backref('tasks', lazy='dynamic'))
    agents = db.relationship('Agent', secondary='agent_task', back_populates='tasks')
    reports = db.relationship('Report', secondary=task_report, back_populates='tasks')
    def __init__(self, name, creator_id, description=None, created_at=None, status="OPEN"):
        self.name = name
        self.description = description
        self.creator_id = creator_id
        self.created_at = created_at or datetime.utcnow()
        self.status = status

class TaskRequest(db.Model):
    __tablename__ = 'task_requests'

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    agent_id = db.Column(db.Integer, db.ForeignKey('agents.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    approved = db.Column(db.Boolean, default=False)

    task = db.relationship('Task', backref=db.backref('assignment_requests', lazy=True))
    agent = db.relationship('Agent', backref=db.backref('task_requests', lazy=True))

    def __init__(self, task_id, agent_id):
        self.task_id = task_id
        self.agent_id = agent_id
