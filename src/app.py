import requests
from flask import Flask, render_template, jsonify, url_for, make_response, request, session, redirect
from flask_login import UserMixin
# from src import create_app
from src.db import db, User, Report
from src.userAPI import user, register_user, login_user
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

from werkzeug.utils import secure_filename
import os
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] ="secretkey"
app.config['UPLOAD_FOLDER'] = 'src/static'
db.init_app(app)


# app.register_blueprint(user)

@app.route('/')
def main():
    if not session.get('logged_in'):
        #TODO This should display "sign in" button in navbar if not logged in
        return render_template('mainpage.html')
    else:
        #TODO This should display "sign out" button in navbar if logged in
        return render_template('mainpage.html')

    # return render_template('mainpage.html')
@app.route('/users')
def get_users():
    return render_template('users.html')
@app.route('/login')
def login():
    return render_template('login.html')


@app.route("/register")
def register():
    return render_template('register.html')
@app.route("/report")
def report():
    return render_template('report.html')
@app.route('/create-report', methods = ['POST'] )
def create_report():
    location = request.form.get('location')
    description = request.form.get('description')
    photo = request.files.get('photo')

    if photo:
        filename = secure_filename(photo.filename)
        photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    else:
        filename = None

    report = Report(location, description, filename)
    db.session.add(report)
    db.session.commit()
    return redirect(url_for('main'))
@app.route('/view-reports')
def view_reports():
    reports = Report.query.all()
    return render_template('reports.html', reports=reports)



if __name__ == '__main__':
    app.run(debug=True)
