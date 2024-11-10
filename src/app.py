import requests
from flask import Flask, render_template, jsonify, url_for, make_response, request, session
from flask_login import UserMixin
# from src import create_app
from src.userAPI import user, register_user, login_user
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] ="secretkey"
db = SQLAlchemy(app)


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

if __name__ == '__main__':
    app.run(debug=True)