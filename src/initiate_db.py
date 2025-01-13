import sys
import os
from sqlalchemy import inspect
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# Add the project directory to the Python path
from src.app import create_app
from src.db import db
from src.models import User, Report,Agent,Manager,Organisation
from src.extensions import bcrypt
from datetime import datetime, timedelta, timezone
import os


app = create_app()


def initiate_db(app):
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()

        print("-------------------\n*INITIALIZING THE DATABASE, POPULATING WITH DUMMY DATA*")
        print("-------------------\n|||||||||||||")

        # Check if the organization already exists
        organisation = Organisation.query.filter_by(token="org_token_123").first()
        if not organisation:
            # Add an organization
            organisation = Organisation(name="Example Organization", token="org_token_123")
            afm = Organisation(name="AFM", token="afm_token_123")
            db.session.add(organisation)
            db.session.add(afm)
            db.session.commit()

        # Add users
        users = [
          User(username='Organisation_Owner', password=bcrypt.generate_password_hash('owner123').decode('utf-8'),
               email='owner@example.com', is_owner=True, organisation_id=organisation.id,
               email_confirmed=True, home_address = '48.205821, 16.383034'),
          User(username='Agent_1', password=bcrypt.generate_password_hash('agent').decode('utf-8'),
               email='agent1@example.com', created_at=datetime.now(timezone.utc) - timedelta(days=5),
               email_confirmed=True, home_address = '48.205821, 16.383034'),
          User(username='agent_2', password=bcrypt.generate_password_hash('agent').decode('utf-8'),
               email='agent2@example.com', created_at=datetime.now(timezone.utc) - timedelta(days=10),
               email_confirmed=True, home_address = '48.406391, 15.600153'),
          User(username='manager_1', password=bcrypt.generate_password_hash('manager').decode('utf-8'),
                 email='manager1@example.com', created_at=datetime.now(timezone.utc) - timedelta(days=3),
                 email_confirmed=True, home_address = '48.205821, 16.383034'),
          User(username='manager_2', password=bcrypt.generate_password_hash('manager').decode('utf-8'),
                 email='manager2@example.com', created_at=datetime.now(timezone.utc) - timedelta(days=3),
                 email_confirmed=True, home_address = '48.406391, 15.600153'),
          User(username='user', password=bcrypt.generate_password_hash('1234').decode('utf-8'),
               email='user@example.com', created_at=datetime.now(timezone.utc) - timedelta(days=7),
               email_confirmed=False, home_address = '48.205821, 16.383034'),
          User(username='user1', password=bcrypt.generate_password_hash('1234').decode('utf-8'),
               email='user1@example.com', created_at=datetime.now(timezone.utc) - timedelta(days=2),
               email_confirmed=True, home_address = '48.406391, 15.600153'),
          User(username='user2', password=bcrypt.generate_password_hash('1234').decode('utf-8'),
               email='user2@example.com', created_at=datetime.now(timezone.utc) - timedelta(days=4),
               email_confirmed=True, home_address = '48.205821, 16.383034'),
          User(username='user3', password=bcrypt.generate_password_hash('1234').decode('utf-8'),
               email='user3@example.com', created_at=datetime.now(timezone.utc) - timedelta(days=6),
               email_confirmed=True, home_address = '48.205821, 16.383034'),
          User(username='user4', password=bcrypt.generate_password_hash('1234').decode('utf-8'),
               email='user4@example.com', created_at=datetime.now(timezone.utc) - timedelta(days=8),
               email_confirmed=True, home_address = '48.406391, 15.600153'),
          User(username='user5', password=bcrypt.generate_password_hash('1234').decode('utf-8'),
               email='user5@example.com', created_at=datetime.now(timezone.utc) - timedelta(days=9),
               email_confirmed=True, home_address = '48.205821, 16.383034'),
          User(username='user6', password=bcrypt.generate_password_hash('1234').decode('utf-8'),
               email='user6@example.com', created_at=datetime.now(timezone.utc) - timedelta(days=12),
               email_confirmed=True, home_address = '48.406391, 15.600153'),
          User(username='user7', password=bcrypt.generate_password_hash('1234').decode('utf-8'),
               email='user7@example.com', created_at=datetime.now(timezone.utc) - timedelta(days=15),
               email_confirmed=True, home_address = '48.205821, 16.383034'),
          User(username='user8', password=bcrypt.generate_password_hash('1234').decode('utf-8'),
                 email='user8@example.com', created_at=datetime.now(timezone.utc) - timedelta(days=20),
                 email_confirmed=True, home_address = '48.406391, 15.600153'),
        ]

        db.session.bulk_save_objects(users)
        db.session.commit()

        for c in range(1, 4):
            users[c].organisation_id = organisation.id

        # Assign roles
        manager = Manager(user_id=4, position='Manager')
        agents = [
            Agent(user_id=2, position='Support Agent'),
            Agent(user_id=3, position='Field Agent'),
        ]

        db.session.add(manager)
        db.session.bulk_save_objects(agents)
        db.session.commit()

        # Add a superadmin user
        superadmin_user = User(
            username='admin',
            password=bcrypt.generate_password_hash('1').decode('utf-8'),
            email=os.getenv('ADMIN_EMAIL'),
            email_confirmed=True,
            home_address = '48.406391, 15.600153',
            organisation_id=afm.id
        )

        db.session.add(superadmin_user)
        db.session.commit()

        superadmin_manager = Manager(user_id=superadmin_user.uid, position='Superadmin Manager')
        db.session.add(superadmin_manager)
        db.session.commit()

        print(f"Superadmin created: {superadmin_user.username}, Email: {superadmin_user.email}")

        # Add reports without approver_id and is_approved
        reports = [
            Report(location='48.2082,16.3738', description='River flooded, many people need assistance', photo_file='photo1.jpg', creator_id=12),
            Report(location='47.8095,13.0550', description='Crazy', photo_file='photo2.jpg', creator_id=7),
            Report(location='47.2692,11.4041', description='Holy shit', photo_file='photo3.jpg', creator_id=10),
            Report(location='47.2260,13.3341', description='OMG', photo_file='photo4.jpg', creator_id=8),
            Report(location='47.2228,13.2950', description='WOW', photo_file='photo5.jpg', creator_id=6),
            Report(location='47.3660,13.4560', description='I want to', photo_file='pic1.jpg', creator_id=7),
            Report(location='47.2100,13.3750', description='No way', photo_file='photo7.jpg', creator_id=9),
            Report(location='47.1600,13.4500', description='Impossible', photo_file='photo8.jpg', creator_id=8),
            Report(location='47.2200,13.4000', description='I can\'t believe my eyes', photo_file='photo9.jpg',
                   creator_id=11),
        ]

        db.session.bulk_save_objects(reports)
        db.session.commit()

        print("-------------------\n*CREATED THE TABLES*")

        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        for table in tables:
            print(table)

        print('-------------------\n|||||||||||||')
        print("-------------------\n*SUCCESSFULLY POPULATED THE ORGANIZATION*")
        print(f"Organization: {organisation.name}, Token: {organisation.token}")
        print("-------------------\n|||||||||||||")
        print("-------------------\n*SUCCESSFULLY POPULATED THE DB WITH USERS*")

        for user in User.query.all():
            print(f"Username: {user.username}, Email: {user.email}, Organization: ")

        print("-------------------\n|||||||||||||")
        print("-------------------\n*SUCCESSFULLY POPULATED THE DB WITH ROLES*")
        print(f"Manager: {manager.user.username}, Position: {manager.position}")

        for agent in Agent.query.all():
            print(f"Agent: {agent.user.username}, Position: {agent.position}")

        print("-------------------\n|||||||||||||")
        print("-------------------\n*SUCCESSFULLY POPULATED THE DB WITH REPORTS*")

        for report in Report.query.all():
            print(f"Location: {report.location}, Description: {report.description}, Photo: {report.photo_file}, "
                  f"Creator: {report.creator.username}, Approver: {report.approver.user.username if report.approver else 'None'}")

        print("-------------------\n|||||||||||||")
if __name__ == '__main__':
    initiate_db(app)

