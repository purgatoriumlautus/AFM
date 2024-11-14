from flask import render_template, request
from src.models import User
from flask_login import login_user, current_user, logout_user
def register_routes(app,db,bcrypt):
    # REGISTER ROUTES
    @app.route('/', methods=['GET', 'POST'])
    def index():
        if current_user.is_authenticated:
            return render_template('mainpage.html')
        else:
            return render_template('mainpage.html')

    #     if not session.get('logged_in'):
    #         # TODO This should display "sign in" button in navbar if not logged in
    #         return render_template('mainpage.html')
    #     else:
    #         # TODO This should display "sign out" button in navbar if logged in
    #         return render_template('mainpage.html')


    @app.route('/users')
    def get_users():
        return render_template('users.html')

    @app.route('/login')
    def show_login():
        return render_template('login.html')

    @app.route('/login/<user_id>')
    def login(user_id):
        user = User.query.get(user_id)
        if user:
            login_user(user)
            return "Success"
        else:
            return "User not found"
    @app.route('/logout')
    def logout():
        logout_user()
        return "Success"

    @app.route("/register")
    def register():
        return render_template('register.html')