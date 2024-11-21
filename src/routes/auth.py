from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_user, logout_user

from src.models import User
from src.db import db
from src.extensions import bcrypt

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    username = request.form['username']
    password = request.form['password']
    user = User.query.filter_by(username=username).first()
    if not user:
        return render_template('login.html',alert_message='Account doesnt exist! Please sign in',
                                   redirect_to='auth.register')

    if user and bcrypt.check_password_hash(user.password, password):
        login_user(user)
        return redirect(url_for('main.mainpage'))
    else:
        return render_template('login.html',alert_message='Password is incorrect')
    
    return "Login Failed"


@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.mainpage'))


@auth.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        existing_user_by_username = User.query.filter_by(username=username).first()
        existing_user_by_email = User.query.filter_by(email=email).first()

        if existing_user_by_username:
            return render_template('register.html', alert_message='Username already exists! Please log in',
                                   redirect_to='auth.login')
        if existing_user_by_email:
            return render_template('register.html', alert_message='Email already exists! Please log in',
                                   redirect_to='auth.login')

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, password=hashed_password, email=email)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('main.mainpage'))
@auth.route("/register_owner", methods=['GET', 'POST'])
def register_owner():
    if request.method == 'GET':
        return render_template('register_owner.html')
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        existing_user_by_username = User.query.filter_by(username=username).first()
        existing_user_by_email = User.query.filter_by(email=email).first()

        if existing_user_by_username:
            return render_template('register.html', alert_message='Username already exists! Please log in',
                                   redirect_to='auth.login')
        if existing_user_by_email:
            return render_template('register.html', alert_message='Email already exists! Please log in',
                                   redirect_to='auth.login')

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, password=hashed_password, email=email, is_owner = True)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('main.mainpage'))
