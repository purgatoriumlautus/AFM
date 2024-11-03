import requests
from flask import Flask, render_template, jsonify
# from user import users
from user import user

app = Flask(__name__)

# USERS DUMMY DATA
users = [{"name":"John","surname":"Doe","email":"123@gmail.com","password":"12345678"}] #dummy data
app.register_blueprint(user)
@app.route('/')
def main():
    return render_template('mainpage.html')
@app.route('/users')
def get_users():
    return render_template('users.html',users=users)

if __name__ == '__main__':
    app.run(debug=True)