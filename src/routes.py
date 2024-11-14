from flask import render_template, request, redirect, url_for
from src.models import User
from flask_login import login_user, current_user, logout_user


# REGISTER ROUTES/ENDPOINTS FOR THE URL

def register_routes(app,db,bcrypt):
    # REGISTER ROUTES
    @app.route('/', methods=['GET', 'POST'])
    def mainpage():
        if current_user.is_authenticated:
            # IF USER IS LOGGED IN
            return render_template('mainpage.html')
        else:
            return render_template('mainpage.html')


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
                return redirect(url_for('mainpage'))
            else:
                return "Login Failed"
    @app.route('/logout')
    def logout():
        logout_user()
        return "Success"

    @app.route("/register", methods=['GET', 'POST'])
    def register():
        if request.method == 'GET':
            return render_template('register.html')
        elif request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            email = request.form['email']

            hashed_password = bcrypt.generate_password_hash(password)

            user = User(username=username, password=hashed_password, email=email)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('mainpage'))
    def register():
        return render_template('register.html')