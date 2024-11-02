from flask import Blueprint,request,jsonify
from werkzeug.security import check_password_hash,generate_password_hash
from .constants.http_status_codes import HTTP_400_BAD_REQUEST,HTTP_409_CONFLICT,HTTP_201_CREATED,HTTP_401_UNAUTHORIZED,HTTP_404_NOT_FOUND,HTTP_200_OK
import validators
from src.db import User,db
from flask_jwt_extended import jwt_required,create_access_token,create_refresh_token,get_jwt_identity

user = Blueprint("user",__name__,url_prefix="/api/v1/user")


@user.post('/register')
def register_user():
    name = request.json['name']
    surname = request.json['surname']
    email = request.json['email']
    password = request.json['password']
    
    
    if len(password)<8:
        return jsonify({"error":"password is too short"}),HTTP_400_BAD_REQUEST 

    #implement other constraints directly on the page using JS

    if not validators.email(email):
        return jsonify({"error":"email is not valid"}),HTTP_400_BAD_REQUEST 


    if User.query.filter_by(email=email).first() is not None:
        return jsonify({"error":"email is taken"}),HTTP_409_CONFLICT 

    pwd_hash = generate_password_hash(password)
    user=User(name=name,surname=surname,password=pwd_hash,email=email)
    db.session.add(user)
    db.session.commit()   

    return jsonify({
        'message':'user created',
        'user':{
            "name":name,
            'surname': surname,
            'email':email,

        }
    }),HTTP_201_CREATED






@user.post("/login")
def login_user():
    email = request.json.get('email','')
    password = request.json.get('password','')
    
    user = User.query.filter_by(email=email).first()

    if user:
        is_pass_correct = check_password_hash(user.password,password)
        if is_pass_correct:
            refresh = create_refresh_token(identity=user.id)
            access = create_access_token(identity=user.id)
            return jsonify({
                'user':{
                    'refresh':refresh,
                    'access':access,
                    'name':user.name,
                    'email':user.email
                }
            })

    return {"error": "wrong credentials"},HTTP_401_UNAUTHORIZED


@user.get("/me")
@jwt_required() #MAKES this route available only for authorized users
def show_profile():
    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()
    return jsonify({'user':
                    {
                        'name':user.name,
                        'surname':user.surname,
                        'email':user.email,
                        'registred_at':user.registred_at
                    }}),HTTP_200_OK


