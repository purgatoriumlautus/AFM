import sys
import os
from sqlalchemy import inspect
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# Add the project directory to the Python path
from src.db import db
from src.models import User, Report
from src.app import create_app
from flask_bcrypt import Bcrypt




app = create_app()
bcrypt = Bcrypt(app)



def initiate_db(app):
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()
        print("-------------------\n*INITIALIZING THE DATA BASE, POPULATING WITH DUMMY DATA*")
        print("-------------------\n|||||||||||||")
        # Add users
        users = [
            User(username='admin', password=bcrypt.generate_password_hash('123').decode('utf-8'), email='@example.com'),
            User(username='Andrew', password=bcrypt.generate_password_hash('1234').decode('utf-8'), email='user1@example.com'),
            User(username='user2', password=bcrypt.generate_password_hash('1234').decode('utf-8'), email='user2@example.com'),
            User(username='user3', password=bcrypt.generate_password_hash('1234').decode('utf-8'), email='user3@example.com'),
            User(username='user4', password=bcrypt.generate_password_hash('1234').decode('utf-8'), email='user4@example.com'),
            User(username='user5', password=bcrypt.generate_password_hash('1234').decode('utf-8'), email='user5@example.com'),
            User(username='user6', password=bcrypt.generate_password_hash('1234').decode('utf-8'), email='user6@example.com'),
            User(username='user7', password=bcrypt.generate_password_hash('1234').decode('utf-8'), email='user7@example.com'),
            User(username='user8', password=bcrypt.generate_password_hash('1234').decode('utf-8'), email='user8@example.com'),
            User(username='user9', password=bcrypt.generate_password_hash('1234').decode('utf-8'), email='user9@example.com'),
            User(username='user10', password=bcrypt.generate_password_hash('1234').decode('utf-8'), email='user10@example.com'),
        ]


        # Add reports
        reports = [
            Report(location='48.2082,16.3738', description='Scary', photo_file='photo1.jpg'),
            Report(location='47.8095,13.0550', description='Crazy', photo_file='photo2.jpg'),
            Report(location='47.2692,11.4041', description='Holy shit', photo_file='photo3.jpg'),
            Report(location='47.2260,13.3341', description='OMG', photo_file='photo4.jpg'),
            Report(location='47.2228,13.2950', description='WOW', photo_file='photo5.jpg'),
            Report(location='47.3660,13.4560', description='I want to', photo_file='pic1.jpg'),
            Report(location='47.2100,13.3750', description='No way', photo_file='photo7.jpg'),
            Report(location='47.1600,13.4500', description='Impossible', photo_file='photo8.jpg'),
            Report(location='47.2200,13.4000', description='I can\'t believe my eyes', photo_file='photo9.jpg'),
        ]
        # Insert data into the database
        db.session.bulk_save_objects(users)
        db.session.bulk_save_objects(reports)
        db.session.commit()
        print("-------------------\n*CREATED THE TABLES*")
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        for table in tables:
            print(table)
        print('-------------------\n|||||||||||||')
        
        print("-------------------\n*SUCCESFULLY POPULATED THE DB WITH USERS*")
        
        users = User.query.all()
        for user in users:
            print(f"Username: {user.username}, Email: {user.email}")
        print("-------------------\n|||||||||||||")

        print("-------------------\n*SUCCESFULLY POPULATED THE DB WITH REPORTS*")
        reports = Report.query.all()
        for report in reports:
            print(f"Location: {report.location}, Description: {report.description}, Photo: {report.photo_file}")
        print("-------------------\n|||||||||||||")


if __name__ == '__main__':
    initiate_db(app)