from flask import render_template, request, redirect, url_for,session
from src.models import User
from flask_login import login_user, current_user, logout_user
from src.db import db
import os
from flask import  render_template,  url_for,  request, session, redirect
from src.models import User, Report
from werkzeug.utils import secure_filename
from flask_bcrypt import bcrypt

# REGISTER ROUTES/ENDPOINTS FOR THE URL

def register_routes(app,db,bcrypt):
    # REGISTER ROUTES
    @app.route('/', methods=['GET', 'POST'])
    def mainpage():
        if current_user.is_authenticated:
            # IF USER IS LOGGED IN
            reports = Report.all_reports()

            return render_template('mainpage.html', reports=reports)
        else:
            reports = Report.all_reports()

        return render_template('mainpage.html', reports=reports)



    @app.route('/users')
    def get_users():
        return render_template('users.html')

   
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'GET':
            return render_template('login.html')
        elif request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            user = User.query.filter(User.username==username).first()
            
            if bcrypt.check_password_hash(user.password, password):
                login_user(user)
                print('log')
                return redirect(url_for('mainpage'))
            else:
                return "Login Failed"
    

    
    @app.route('/logout')
    def logout():
        logout_user()
        return redirect(url_for('mainpage'))


    @app.route("/register", methods=['GET', 'POST'])
    def register():
        if request.method == 'GET':
            return render_template('register.html')
        elif request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            email = request.form['email']

            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

            user = User(username=username, password=hashed_password, email=email)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for('mainpage'))

    


    
    

    

    @app.route('/create-report', methods = ['GET','POST'] )
    def create_report():
        if request.method == "GET":
            return(render_template('report.html'))
        location = request.form.get('location')
        description = request.form.get('description')
        photo = request.files.get('photo')

        if photo:
            filename = secure_filename(photo.filename)
            photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            photo.save(photo_path)
        else:
            filename = None

        report = Report(location, description, filename)
        db.session.add(report)
        db.session.commit()
        return redirect(url_for('mainpage'))
    

    @app.route('/view-reports')
    def view_reports():
        reports = Report.query.all()
        return render_template('reports.html', reports=reports)