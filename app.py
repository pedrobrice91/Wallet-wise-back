from flask import Flask, jsonify, request
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt
from flask_bcrypt import Bcrypt
from models import db, User, Type_of_movement, Transaction, Movement_goal, Movement, Goal, Account, Category
from utils import is_valid_email, is_valid_password, find_user_by_email, hash_password, check_password
from flask_cors import CORS
import jwt
from functools import wraps
import os
from datetime import timedelta, datetime


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

 #aqui comienza
@app.route("/type_of_movements", methods=["GET"]) #Read
def get_type_of_movements():
    type_of_movements = Type_of_movement.query.all()
    print(type_of_movements[0].serialize())
    type_of_movements = list (map(lambda type_of_movement: type_of_movement.serialize(), type_of_movements))
    return jsonify(type_of_movements)

@app.route("/type_of_movement", methods=["POST"])#Create
def type_of_movement():
        data = request.get_json()
        
        if isinstance(data, list):
            if len(data) == 0:
                return jsonify({"error": "No se proporcionaron datos"}), 400
            data = data[0]
        
        if "name" not in data:
            return jsonify({"error": "El campo 'name' es requerido"}), 400
        
        type_of_movement = Type_of_movement()
        type_of_movement.name = data["name"]

        db.session.add(type_of_movement)
        db.session.commit()

        return jsonify({"msg": "Tipo de movimiento creado"}), 201

@app.route("/type_of_movement/<int:type_of_movements_id>", methods=["PUT", "DELETE"])
def update_type_of_movement(type_of_movements_id):
        return jsonify({"msg": "Transacción creada"}), 201

@app.route("/categorys", methods=["GET"])#Read
def get_category():
    category = Category.query.all()
    category = list(map(lambda category:category.serialize(), category))
    return jsonify(category)

@app.route("/category/<int:category_id>", methods=["PUT", "DELETE"])
def update_category(category_id):
        category = Category.query.get(category_id)

        if category is None:
            return jsonify("category not found"), 404
        
        if request.method == "PUT": #Update
            data = request.get_json()
            
            if data.get("name"):           
                category.name = data["name"]

            if data.get("type_of_movement_id"):
                category.type_of_movement_id = data["type_of_movement_id"]
          
            db.session.commit()
            return jsonify(category.serialize()), 200

        if request.method == "DELETE":  # Delete
            db.session.delete(category)
            db.session.commit()
            return jsonify(f"Category {category_id} deleted"), 200
#transacciones
@app.route("/category", methods=["POST"])#Create
def category():
    
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No se proporcionaron datos"}), 400
        
        category = Category()
        
        if "name" not in data or "type_of_movement_id" not in data:
            return jsonify({"error": "Faltan campos requeridos (name o type_of_movement_id)"}), 400
        
        category.name = data["name"]
        category.type_of_movement_id = data["type_of_movement_id"]
        
        db.session.add(category)
        db.session.commit()

        return jsonify({"msg": "Transacción creada"}), 201

@app.route("/transactions", methods=["GET"])#Read
def get_transaction():
    transaction = Transaction.query.all()
    transaction = list(map(lambda transaction:transaction.serialize(), transaction))
    return jsonify(transaction)

@app.route("/transaction", methods=["POST"])#Create
def transaction():
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No se proporcionaron datos"}), 400
        
        transaction = Transaction()
        
        if "name" not in data or "category_id" not in data:
            return jsonify({"error": "Faltan campos requeridos (name o category_id)"}), 400
        
        transaction.name = data["name"]
        transaction.category_id = data["category_id"]
        
        db.session.add(transaction)
        db.session.commit()

        return jsonify({"msg": "Transacción creada"}), 201

@app.route("/transaction/<int:transaction_id>", methods=["PUT", "DELETE"])
def update_transaction(transaction_id):
        transaction = Transaction.query.get(transaction_id)
        
        if transaction is None:
            return jsonify("Transaction not found"), 404
        
        if request.method == "PUT": #Update
            data = request.get_json()

            if data.get("name"):
                transaction.name = data["name"]

            if data.get("category_id"):
                transaction.category_id = data["category_id"]

            db.session.commit()
            return jsonify(transaction.serialize()), 200

        if request.method == "DELETE":  #Delete
            db.session.delete(transaction)
            db.session.commit()
            return jsonify(f"transaction {transaction_id} deleted"), 200

#aqui termina 
 
@app.route('/add-movement', methods=['POST'])
@jwt_required()
def add_movement():
    try:
        user_id = get_jwt_identity() 
        
        data = request.get_json()
        amount = data.get('amount')
        transaction_date = data.get('transaction_date')
        account_id = data.get('account_id')
        transaction_id = data.get('transaction_id')
        
        if not all([amount, transaction_date, account_id, transaction_id]):
            return jsonify({"error": "Missing required fields"}), 400
        
        transaction_date = datetime.strptime(transaction_date, '%Y-%m-%d')
        
        new_movement = Movement(
            amount=amount,
            transaction_date=transaction_date,
            account_id=account_id,
            transaction_id=transaction_id,
            created_at=datetime.now()
        )
        
        db.session.add(new_movement)
        db.session.commit()
        
        return jsonify({"message": "Movement added successfully", "movement": new_movement.serialize()}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="localhost", port=5050, debug=True)