from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from src.models import User
from src.db import db
from src.extensions import bcrypt,mail
from flask_mail import Mail, Message
import re  # Import for password validation
import os

auth = Blueprint('auth', __name__)




def is_super_admin():
    sup_email = os.getenv('ADMIN_EMAIL')
    return sup_email == current_user.email



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
    if not user.email_confirmed:
        flash('Email is not confirmed.', 'danger')
        return redirect(url_for('auth.login'))
    if user and bcrypt.check_password_hash(user.password, password):
        login_user(user)
        if user.is_banned:
            flash('Access restricted, you are banned!', 'danger')
            return redirect(url_for('main.mainpage'))
        
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
        coordinates = request.form.get('coordinates')
        # Enforce password strength
        if len(password) < 8 or not re.search(r'[A-Z]', password) or not re.search(r'[a-z]', password) or not re.search(r'[0-9]', password) :
            flash('Password must be at least 8 characters long and include an uppercase letter, a lowercase letter, a digit', 'danger')
            return redirect(url_for('auth.register'))
        
        if not coordinates:
            flash('Coordinates are required. Please select a location on the map or find the address', 'danger')
            return redirect(url_for('auth.register'))

        # Check if username or email already exists
        existing_user_by_username = User.query.filter_by(username=username).first()
        existing_user_by_email = User.query.filter_by(email=email).first()

        if existing_user_by_username:
            flash('Username already exists! Please log in.', 'danger')
            return redirect(url_for('auth.login'))
        if existing_user_by_email:
            flash('Email already exists! Please log in.', 'danger')
            return redirect(url_for('auth.login'))

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, password=hashed_password, email=email,home_address=coordinates)
        db.session.add(user)
        db.session.commit()
        verification_link = url_for('auth.verify_email', user_id=user.uid, _external=True)

        # Send the verification email
        msg = Message(
            sender = ('AFM Team, afm.team.contact@gmail.com'),
            subject='AFM Account Verification',
            recipients=[email],
            body=f'This is the plain text version of the email. Verify your account: {verification_link}',
            html=f"""
                        <html>
                            <body>
                                <h1">Verify Your Account</h1>
                                <p>Dear {username}, thank you for signing up with <strong>AFM</strong>!</p>
                                <p>Please click the link below to verify your email address and activate your account:</p>
                                <p><a href="{verification_link}" style="color:blue; font-weight:bold;">Verify My Account</a></p>
                                <p><br>The AFM Team</p>
                            </body>
                        </html>
                    """
        )
        mail.send(msg)

        flash('A verification email has been sent. Please check your inbox.', 'info')
        return redirect(url_for('auth.login'))

@auth.route("/verify/<int:user_id>", methods=['GET'])
def verify_email(user_id):
    user = User.query.get_or_404(user_id)
    if user.email_confirmed:
        flash('Your email is already verified.', 'success')
    else:
        user.email_confirmed = True
        db.session.commit()
        flash('Your email has been successfully verified!', 'success')

    return redirect(url_for('auth.login'))


@auth.route("/register_owner", methods=['GET', 'POST'])
def register_owner():
    if request.method == 'GET':
        return render_template('register_owner.html')

    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        # Enforce password strength for owners as well
        if len(password) < 8 or not re.search(r'[A-Z]', password) or not re.search(r'[a-z]', password) or not re.search(
                r'[0-9]', password) or not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            flash(
                'Password must be at least 8 characters long and include an uppercase letter, a lowercase letter, a digit, and a special character.',
                'danger')
            return redirect(url_for('auth.register_owner'))


        existing_user_by_username = User.query.filter_by(username=username).first()
        existing_user_by_email = User.query.filter_by(email=email).first()

        if existing_user_by_username:
            flash('Username already exists! Please log in.', 'danger')
            return redirect(url_for('auth.login'))
        if existing_user_by_email:
            flash('Email already exists! Please log in.', 'danger')
            return redirect(url_for('auth.login'))

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        user = User(username=username, password=hashed_password, email=email, is_owner=True,
                    email_confirmed=False)
        db.session.add(user)
        db.session.commit()


        verification_link = url_for('auth.verify_email', user_id=user.uid, _external=True)
        msg = Message(
            sender='AFM Team <afm.team.contact@gmail.com>',
            subject='AFM Account Verification',
            recipients=[email],
            body=f'This is the plain text version of the email. Verify your account: {verification_link}',
            html=f"""
                <html>
                    <body>
                        <h1>Verify Your Account</h1>
                        <p>Thank you for signing up with <strong>AFM</strong>!</p>
                        <p>Please click the link below to verify your email address and activate your account:</p>
                        <p><a href="{verification_link}" style="color:blue; font-weight:bold;">Verify My Account</a></p>
                        <p><br>The AFM Team</p>
                    </body>
                </html>
            """
        )
        mail.send(msg)

        flash('A verification email has been sent. Please check your inbox to activate your account.', 'info')

        return redirect(url_for('auth.login'))
    

@auth.route('/profile/<username>', methods=['GET'])
@login_required
def profile(username): # can be modified so that admins can see profiles of other users
    if current_user.username != username: # if another user tries to access the profile, redirect to main page
        flash('You are not authorized to view this profile.', 'danger')
        return redirect(url_for('main.mainpage'))
    return render_template('profile.html', user=current_user,is_super_admin=is_super_admin())


@auth.route('/profile/<username>/edit', methods=['GET', 'POST'])
@login_required
def edit_profile(username):
    if current_user.username != username:
        flash('You are not authorized to view this profile.', 'danger')
        return redirect(url_for('main.mainpage'))
    if request.method == 'POST':
        current_user.username = request.form['username']
        current_user.password = request.form['email']
        db.session.commit()
        flash('Profile was updated successfully!', 'success')
        return redirect(url_for('auth.profile', username=current_user.username,is_super_admin=is_super_admin()))
    

    return render_template('edit_profile.html', user=current_user,is_super_admin=is_super_admin())

