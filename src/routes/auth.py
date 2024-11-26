from flask import Blueprint, render_template, request, redirect, url_for, flash
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
        flash('Account doesn\'t exist! Please register.', 'danger')
        return redirect(url_for('auth.register'))

    if user and bcrypt.check_password_hash(user.password, password):
        login_user(user)
        flash('Logged in successfully!', 'success')
        return redirect(url_for('main.mainpage'))
    else:
        flash('Password is incorrect.', 'danger')
        return redirect(url_for('auth.login'))


@auth.route('/logout')
def logout():
    logout_user()
    flash('Signed out successfully.', 'info')
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
            flash('Username already exists! Please log in.', 'danger')
            return redirect(url_for('auth.login'))
        if existing_user_by_email:
            flash('Email already exists! Please log in.', 'danger')
            return redirect(url_for('auth.login'))

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, password=hashed_password, email=email)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash('Account created successfully!', 'success')
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
            flash('Username already exists! Please log in.', 'danger')
            return redirect(url_for('auth.login'))
        if existing_user_by_email:
            flash('Email already exists! Please log in.', 'danger')
            return redirect(url_for('auth.login'))

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, password=hashed_password, email=email, is_owner=True)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash('Owner account created successfully!', 'success')
        return redirect(url_for('main.mainpage'))