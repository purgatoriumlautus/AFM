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
    email_confirmed = db.Column(db.Boolean, default=False)
    is_superadmin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    organisation_id = db.Column(
        db.Integer,
        db.ForeignKey('organisations.id', name='fk_user_organisation_id',ondelete='SET NULL'),
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
        db.UniqueConstraint('organisation_id', 'is_owner', name='unique_owner_organisation'),
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

    user = db.relationship('User', back_populates='manager')

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
    approver_id = db.Column(db.Integer, db.ForeignKey('managers.id', ondelete="SET NULL"), nullable=True)

    creator = db.relationship('User', back_populates='report')
    approver = db.relationship('Manager', backref='approved_reports')

    def __init__(self, location, description, photo_file=None, creator_id=None, approver_id=None, is_approved=False):
        self.location = location
        self.description = description
        self.photo_file = photo_file
        self.creator_id = creator_id
        self.is_approved = is_approved

    @staticmethod
    def all_reports():
        return Report.query.all()


class Organisation(db.Model):
    __tablename__ = 'organisations'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    token = db.Column(db.String(100), unique=True, nullable=True)  # Link token for invites
    owner_id = db.Column(
        db.Integer,
        db.ForeignKey('users.uid', name='fk_organisation_owner_id', ondelete="CASCADE"),  # Enable CASCADE deletion
        nullable=True
    )

    # Relationships
    users = db.relationship(
        'User',
        back_populates='organisation',
        foreign_keys='User.organisation_id',
        lazy='dynamic'
    )
    owner = db.relationship(
        'User',
        foreign_keys=[owner_id],
        backref='owned_organisation',
        uselist=False
    )

    __table_args__ = (
        db.UniqueConstraint('id', name='unique_organisation_id'),
    )

    def __repr__(self):
        return f'<Organisation {self.name}>'
