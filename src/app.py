from flask import Flask, render_template
# from user import users

app = Flask(__name__)

# USERS DUMMY DATA
users = [{"name":"John","surname":"Doe","email":"123@gmail.com","password":"12345678"}] #dummy data

@app.route('/')
def index():
    return render_template('index.html')
@app.route('/users')
def get_users():
    return render_template('users.html',users=users)

if __name__ == '__main__':
    app.run(debug=True)