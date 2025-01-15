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
        
          afm = Organisation(name="AFM", token="afm_token_123")
          organisation = Organisation(name="Example Organization", token="org_token_123")
          db.session.add(afm)
          db.session.add(organisation)
          
          db.session.commit()

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
          # Add users
          users = [
          #Add additional owner From vienna
          User(username='org_owner', password=bcrypt.generate_password_hash('123').decode('utf-8'),
               email='owner@example.com', is_owner=True, organisation_id=organisation.id,
               email_confirmed=True, home_address = '48.22320735566559,16.38919266672499'),
          
          #Add Three agents in AFM IN KREMS
          User(username='agent_afm_1', password=bcrypt.generate_password_hash('123').decode('utf-8'),
               email='agentafm1@example.com', created_at=datetime.now(timezone.utc) - timedelta(days=5),
               email_confirmed=True, home_address = '48.408203429499316,15.587987069854968',organisation_id= 1),

          User(username='agent_afm_2', password=bcrypt.generate_password_hash('123').decode('utf-8'),
               email='agentafm2@example.com', created_at=datetime.now(timezone.utc) - timedelta(days=10),
               email_confirmed=True, home_address = '48.408203429499316,15.587987069854968',organisation_id= 1),
          
          User(username='agent_afm_3', password=bcrypt.generate_password_hash('123').decode('utf-8'),
               email='agentafm3@example.com', created_at=datetime.now(timezone.utc) - timedelta(days=10),
               email_confirmed=True, home_address = '48.408203429499316,15.587987069854968' ,organisation_id= 1),
          
          
          #Add Managers to afm
          User(username='manager_afm_1', password=bcrypt.generate_password_hash('123').decode('utf-8'),
                 email='managerafm1@example.com', created_at=datetime.now(timezone.utc) - timedelta(days=3),
                 email_confirmed=True, home_address = '48.408203429499316,15.587987069854968',organisation_id= 1),
          User(username='manager_afm_2', password=bcrypt.generate_password_hash('123').decode('utf-8'),
                 email='managerafm2@example.com', created_at=datetime.now(timezone.utc) - timedelta(days=3),
                 email_confirmed=True, home_address = '48.408203429499316,15.587987069854968',organisation_id= 1),
          User(username='manager_afm_3', password=bcrypt.generate_password_hash('123').decode('utf-8'),
                 email='managerafm3@example.com', created_at=datetime.now(timezone.utc) - timedelta(days=3),
                 email_confirmed=True, home_address = '48.408203429499316,15.587987069854968',organisation_id= 1),
          

          #Add agents to external org
          User(username='agent_1', password=bcrypt.generate_password_hash('1234').decode('utf-8'),
               email='agent1@example.com', created_at=datetime.now(timezone.utc) - timedelta(days=7),
               email_confirmed=False, home_address = '48.22320735566559,16.38919266672499',organisation_id= 2),

          User(username='agent_2', password=bcrypt.generate_password_hash('1234').decode('utf-8'),
               email='agent2@example.com', created_at=datetime.now(timezone.utc) - timedelta(days=2),
               email_confirmed=True, home_address = '48.22320735566559,16.38919266672499',organisation_id= 2),

          User(username='agent_3', password=bcrypt.generate_password_hash('1234').decode('utf-8'),
               email='agent3@example.com', created_at=datetime.now(timezone.utc) - timedelta(days=4),
               email_confirmed=True, home_address = '48.22320735566559,16.38919266672499',organisation_id= 2),


          #Add managers to external org
          User(username='manager1', password=bcrypt.generate_password_hash('123').decode('utf-8'),
                 email='manager1@example.com', created_at=datetime.now(timezone.utc) - timedelta(days=3),
                 email_confirmed=True, home_address = '48.22320735566559,16.38919266672499',organisation_id= 2),
          User(username='manager2', password=bcrypt.generate_password_hash('123').decode('utf-8'),
                 email='manager2@example.com', created_at=datetime.now(timezone.utc) - timedelta(days=3),
                 email_confirmed=True, home_address = '48.22320735566559,16.38919266672499',organisation_id= 2),
          User(username='manager3', password=bcrypt.generate_password_hash('123').decode('utf-8'),
                 email='manager3@example.com', created_at=datetime.now(timezone.utc) - timedelta(days=3),
                 email_confirmed=True, home_address = '48.22320735566559,16.38919266672499',organisation_id= 2),

          #Add regular citizens from krems
          User(username='krems1', password=bcrypt.generate_password_hash('123').decode('utf-8'),
               email='user3@example.com', created_at=datetime.now(timezone.utc) - timedelta(days=6),
               email_confirmed=True, home_address = '48.4106533407932,15.600607878196742'),
          
          User(username='krems2', password=bcrypt.generate_password_hash('123').decode('utf-8'),
               email='krems2@example.com', created_at=datetime.now(timezone.utc) - timedelta(days=6),
               email_confirmed=True, home_address = '48.4106533407932,15.600607878196742'),
          
          User(username='krems3', password=bcrypt.generate_password_hash('123').decode('utf-8'),
               email='krems3@example.com', created_at=datetime.now(timezone.utc) - timedelta(days=6),
               email_confirmed=True, home_address = '48.4106533407932,15.600607878196742'),
          

          


          #regular citizens from vienna
          User(username='vienna1', password=bcrypt.generate_password_hash('123').decode('utf-8'),
               email='vienna1@example.com', created_at=datetime.now(timezone.utc) - timedelta(days=12),
               email_confirmed=True, home_address = '48.22320735566559,16.38919266672499'),
          User(username='vienna2', password=bcrypt.generate_password_hash('123').decode('utf-8'),
               email='vienna2@example.com', created_at=datetime.now(timezone.utc) - timedelta(days=12),
               email_confirmed=True, home_address = '48.22320735566559,16.38919266672499'),
          User(username='vienna3', password=bcrypt.generate_password_hash('123').decode('utf-8'),
               email='vienna3@example.com', created_at=datetime.now(timezone.utc) - timedelta(days=12),
               email_confirmed=True, home_address = '48.22320735566559,16.38919266672499'),

          #One additional from salzburg
          User(username='salzburg', password=bcrypt.generate_password_hash('123').decode('utf-8'),
               email='salzburg@example.com', created_at=datetime.now(timezone.utc) - timedelta(days=12),
               email_confirmed=True, home_address = '47.79788857679537,13.039221505621096'),

        ]

          db.session.bulk_save_objects(users)
          db.session.commit()

          agents = [
               Agent(user_id=3, position='Support Agent'),
               Agent(user_id=4, position='Field Agent'),
               Agent(user_id=5, position='Car Driver'),
               Agent(user_id=9, position='Firefighter'),
               Agent(user_id=10, position=''),
               Agent(user_id=11, position='Geographical Expret'),

          ]

          managers = [
               Manager(user_id=6, position='Manager'),
               Manager(user_id=7, position='Manager'),
               Manager(user_id=8, position='Manager'),
               Manager(user_id=12, position='Manager'),
               Manager(user_id=13, position='Manager'),
               Manager(user_id=14, position='Manager'),

               ]
          

          db.session.bulk_save_objects(managers)
          db.session.bulk_save_objects(agents)
          db.session.commit()

        # Add a superadmin user
          

          print(f"Superadmin created: {superadmin_user.username}, Email: {superadmin_user.email}")

          # Add reports without approver_id and is_approved
          reports = [
               Report(location='48.40298,15.58912', description='River flooded, many people need assistance', photo_file='krems1.jpg', creator_id=15),
               Report(location='48.404009730022096,15.643635104977013', description='Near the bridge my car is drowned.', photo_file='krems2.jpg', creator_id=16),
               Report(location='48.41483492069605,15.604141410214288', description='Many people need help to escape!', photo_file='krems3.jpg', creator_id=17),
               Report(location='48.399679008513246,15.577964808002703', description='People can not drive the cars through. I can not leave the city', photo_file='krems4.jpg', creator_id=15),
               Report(location='48.24863675793549,16.407222776856855', description='Rain does not stop.', photo_file='vienna1.jpg', creator_id=18),
               Report(location='48.228285670642414,16.40069854047639', description='People need help to move their cars', photo_file='vienna2.jpg', creator_id=19),
               Report(location='48.21776395759386,16.432967857715948', description='Stadtpark water levels are rising!', photo_file='vienna3.jpg', creator_id=20),
               Report(location='48.234003085840655,16.359491326207017', description='Vienna is flooded', photo_file='vienna4.jpg', creator_id=18),
               Report(location='47.84459282337878,13.011840339305529', description='Nothing happens in Salzburg!', photo_file='salzburg1.jpg',
                    creator_id=15),
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

