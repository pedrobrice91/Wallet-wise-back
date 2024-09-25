from flask import Flask, jsonify, request
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt
from flask_bcrypt import Bcrypt
from models import db, User, Type_of_movement, Transaction, Movement_goal, Movement, Goal, Account, Category
from utils import is_valid_email, is_valid_password, find_user_by_email, hash_password, check_password
from flask_cors import CORS
from functools import wraps
import os
from datetime import timedelta


app = Flask(__name__) 
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///wallet-wise.db"
app.config["JWT_SECRET_KEY"] = "secret_key"
app.config["SECRET_KEY"] = "contrasena-super-segura"
JWTManager(app)
bcrypt = Bcrypt(app)
db.init_app(app)
Migrate(app, db)
CORS(app)


@app.route("/user", methods=["POST"])
def user():
    data = request.get_json()

    first_name = data.get("first_name")
    last_name = data.get("last_name")
    email = data.get("email")
    password = data.get("password")

    if not email or not is_valid_email(email):
        return jsonify({"msg": "Invalid email format"}), 400

    if find_user_by_email(email):
        return jsonify({"msg": "This email address is already registered"}), 409

    if not password or not is_valid_password(password):
        return jsonify({"msg": "Invalid password format"}), 400

    user = User()
    user.email = email
    user.password = hash_password(password, bcrypt)
    user.first_name = first_name
    user.last_name = last_name

    db.session.add(user)
    db.session.commit()

    additional_claims = {"user_id": user.id}
    access_token = create_access_token(identity=data["email"], additional_claims=additional_claims)
 
    return jsonify({
        "msg": "Success",
            "access_token": access_token,
            "user_id": user.id,
            "user_first_name": user.first_name,
            "user_last_name": user.last_name
    }), 201


@app.route("/login_google", methods=["POST"])
def login_google():
    #comprobar que la información del front llegue al backend
    data = request.get_json()
    expires = timedelta(days=3)    
    user = User.query.filter_by(email=data["email"]).first()
   
    if user is not None:
        additional_claims = {"user_id": user.id}
        access_token = create_access_token(identity=data["email"], additional_claims=additional_claims, expires_delta=expires)
 
        return jsonify({
            "msg":"Success",
            "access_token": access_token,
        }), 200
    else:
        user = User()
        
        user.first_name = data["first_name"]
        user.last_name = data["last_name"]
        user.email = data["email"]

        db.session.add(user)
        db.session.commit()

        additional_claims = {"user_id": user.id}
        access_token = create_access_token(identity=data["email"], additional_claims=additional_claims, expires_delta=expires)
        print(access_token)
        return jsonify({
            "first_name": data["first_name"],
            "last_name": data["last_name"],
            "email": data["email"],
            "access_token": access_token,
        }), 201

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    expires = timedelta(days=3)

    if not email or not is_valid_email(email):
        return jsonify({"msg": "Invalid email format"}), 400
    
    user = find_user_by_email(email)
    if user and check_password(user.password, password, bcrypt):
        additional_claims = {"user_id": user.id}
        access_token = create_access_token(identity=data["email"], additional_claims=additional_claims, expires_delta=expires)

        return jsonify({
            "msg": "Success",
            "access_token": access_token,
            "user_id": user.id,
            "user_first_name": user.first_name,
            "user_last_name": user.last_name
        }), 200
    return jsonify({"msg": "Invalid username or password"}), 401

@app.route("/users", methods=["GET"]) #Read
@jwt_required()
def get_users():
    users = User.query.all()
    users = list(map(lambda user: user.serialize(), users))
    
    return jsonify(users)

@app.route("/user/<int:user_id>", methods=["PUT", "DELETE"])
def update_user(user_id):
        user = User.query.get(user_id)

        if user is None:
            return jsonify("User not found"), 404
        
        if request.method == "PUT": #Update
            data = request.get_json()

            if data.get("email"):
               return jsonify("The email can't be updated"), 400
            
            if data.get("first_name"):           
                user.first_name = data["first_name"]

            if data.get("last_name"):
                user.last_name = data["last_name"]

            if data.get("password"):
                user.password = data["password"]
          
            db.session.commit()
            return jsonify(user.serialize()), 200

        if request.method == "DELETE":  # Delete
            db.session.delete(user)
            db.session.commit()
            return jsonify(f"User {user_id} deleted"), 200
          
@app.route("/account", methods=["GET", "POST"])
@jwt_required()
def account():
    claims = get_jwt()
    user_id = claims.get("user_id")

    if not user_id:
        return jsonify({"msg": "Invalid token"}), 401
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 403

    if request.method == "GET":
        accounts = Account.query.filter_by(user_id=user_id).all()
        accounts = list(map(lambda account: account.serialize(), accounts))
        return jsonify(accounts), 200
    
    if request.method == "POST":
        data = request.get_json()
        account = Account()
        account.name = data["name"]
        account.user_id = user_id
        account.state = True

        db.session.add(account)
        db.session.commit()
        return jsonify(
            {"Msg": "Account created successfully"}
        ), 201
    
@app.route("/account/<int:account_id>", methods=["DELETE"])
@jwt_required()
def delete_account(account_id):
    claims = get_jwt()
    user_id = claims.get("user_id")
 
    account = Account.query.filter_by(id=account_id, user_id=user_id).first()
    if account:
        db.session.delete(account)
        db.session.commit()
        return jsonify({"msg": "Account deleted"}), 200
    else:
        return jsonify({"msg": "Account not found"}), 404
    
@app.route("/account/state/<int:account_id>", methods=["PUT"])
@jwt_required()
def update_state_flow(account_id):
    account = Account.query.filter_by(id=account_id).first()
    if account is None:
        return jsonify({"error": "Account not found"}), 404
            
    account.state = not account.state    
    db.session.commit()
    return jsonify(account.serialize()), 200
 

if __name__ == "__main__":
    app.run(host="localhost", port=5050, debug=True)