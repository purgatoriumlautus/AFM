from flask import Blueprint,request,jsonify
from werkzeug.security import check_password_hash,generate_password_hash
from src.constants.http_status_codes import HTTP_400_BAD_REQUEST,HTTP_409_CONFLICT,HTTP_201_CREATED,HTTP_401_UNAUTHORIZED,HTTP_404_NOT_FOUND,HTTP_200_OK #STATUS CODES FOR RETURNING TO THE USERS, CHECK constants
import validators
from src.db import User,db
from flask_jwt_extended import jwt_required,create_access_token,create_refresh_token,get_jwt_identity

#class User: Should be created?
user = Blueprint("user",__name__,url_prefix="/user")  #create user blueprint

# THIS IS DATABASE QUERRY that needs to be implemented in the future

@user.post('/register') #set the post method for /register route
def register_user(): #register function
    #retrieve all the neccecary data from the post requst
    name = request.json['name']
    surname = request.json['surname']
    email = request.json['email']
    password = request.json['password']

    #few short cheks, should be replaced by more advanced in the future
    if len(password)<8:
        return jsonify({"error":"password is too short"}),HTTP_400_BAD_REQUEST

    #implement other constraints directly on the page using JS

    if not validators.email(email):
        return jsonify({"error":"email is not valid"}),HTTP_400_BAD_REQUEST

    #query for checking if a user with the same email exists
    if User.query.filter_by(email=email).first() is not None:
        return jsonify({"error":"email is taken"}),HTTP_409_CONFLICT


    #encrypt the password
    pwd_hash = generate_password_hash(password)
    #create the user instance
    user=User(name=name,surname=surname,password=pwd_hash,email=email)
    #add the user to db
    db.session.add(user)
    db.session.commit()

    #return success message
    return jsonify({
        'message':'user created',
        'user':{
            "name":name,
            'surname': surname,
            'email':email,

        }
    }),HTTP_201_CREATED


#login
@user.post("/login")
def login_user():

    #retrieve the data from user's request
    email = request.json.get('email','')
    password = request.json.get('password','')

    #query to get the user by the email
    user = User.query.filter_by(email=email).first()

    #if user exists
    if user:
        #check password correctency
        is_pass_correct = check_password_hash(user.password,password)
        #if correct ->
        if is_pass_correct:
            #create jwt refresh token used for (refreshing an access token)
            refresh = create_refresh_token(identity=user.id) #set the identity to user_id so it can be retrieved later on

            #create jwt access token (used for authentification)
            access = create_access_token(identity=user.id) #set the identity to user_id so it can be retrieved later on

            return jsonify({
                'user':{
                    'refresh':refresh,
                    'access':access,
                    'name':user.name,
                    'email':user.email
                }
            })

    return {"error": "wrong credentials"},HTTP_401_UNAUTHORIZED



#simple example of page for which the user have to log in
@user.get("/me")
@jwt_required() #MAKES this route available only for authorized users
def show_profile():

    user_id = get_jwt_identity() #returns user_id as we set above
    user = User.query.filter_by(id=user_id).first() #query to get the user by id
    return jsonify({'user':
                    {
                        'name':user.name,
                        'surname':user.surname,
                        'email':user.email,
                        'registred_at':user.registred_at
                    }}),HTTP_200_OK


