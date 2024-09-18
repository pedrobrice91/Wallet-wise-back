from flask import Flask, jsonify, request
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from flask_bcrypt import Bcrypt
from models import db, User, Type_of_movement, Transaction, Movement_goal, Movement, Goal, Account, Category
from utils import is_valid_email, is_valid_password, find_user_by_email, hash_password, check_password
from flask_cors import CORS

app = Flask(__name__) 
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///wallet-wise.db"
app.config["JWT_SECRET_KEY"] = "secret_key"
app.config["SECRET_KEY"] = "contrasena-super-segura"
JWTManager(app)
bcrypt = Bcrypt(app)
db.init_app(app)
Migrate(app, db)
CORS(app)

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not is_valid_email(email):
        return jsonify({"msg": "Invalid email format"}), 400
    
    user = find_user_by_email(email)
    if user and check_password(user.password, password, bcrypt):
        access_token = create_access_token(identity=email)
        return jsonify({"msg": "Éxito", "access_token": access_token}), 200
    return jsonify({"msg": "invalid username or password"}), 200

@app.route("/user", methods=["POST"])#Create
def user():
    data = request.get_json()
    user = User()
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    email = data.get("email")
    password = data.get("password")

    if not email or not is_valid_email(email):
        return jsonify({"msg": "Correo invalido"}), 400

    if find_user_by_email(email):
        return jsonify({"msg": "El usuario ya existe"}), 400

    if not password or not is_valid_password(password):
        return jsonify({"msg": "Contraseña invalida"}), 400

    user.email = email
    user.password = hash_password(password, bcrypt)
    user.first_name = first_name
    user.last_name = last_name

    db.session.add(user)
    db.session.commit()

    return jsonify({"msg": "Usuario creado"}), 201

@app.route("/users", methods=["GET"]) #Read
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
#tipo de movimiento
@app.route("/type_of_movements", methods=["GET"]) #Read
def get_type_of_movements():
    type_of_movements = Type_of_movement.query.all()
    type_of_movements = list (map(lambda type_of_movement: type_of_movement.serialize(), type_of_movements))
    return jsonify(type_of_movements)

@app.route("/type_of_movement", methods=["POST"]) #Create
def type_of_movement():
    data = request.get_json()
    user = User()
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    email = data.get("email")
    password = data.get("password")

    if not email or not is_valid_email(email):
        return jsonify({"msg": "Correo invalido"}), 400

    if find_user_by_email(email):
        return jsonify({"msg": "El usuario ya existe"}), 400

    if not password or not is_valid_password(password):
        return jsonify({"msg": "Contraseña invalida"}), 400

    user.email = email
    user.password = hash_password(password, bcrypt)
    user.first_name = first_name
    user.last_name = last_name

    db.session.add(user)
    db.session.commit()

    return jsonify({"msg": "Usuario creado"}), 201
    
@app.route("/type_of_movement/<int:type_of_movements_id>", methods=["PUT", "DELETE"])
def update_type_of_movement(type_of_movements_id):
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
#transacciones
@app.route("/transactions", methods=["GET"]) #Read
def get_transaction():
    type_of_movements = Type_of_movement.query.all()
    type_of_movements = list (map(lambda type_of_movement: type_of_movement.serialize(), type_of_movements))
    return jsonify(type_of_movements)

@app.route("/transaction", methods=["POST"]) #Create
def transaction():
    data = request.get_json()
    user = User()
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    email = data.get("email")
    password = data.get("password")

    if not email or not is_valid_email(email):
        return jsonify({"msg": "Correo invalido"}), 400

    if find_user_by_email(email):
        return jsonify({"msg": "El usuario ya existe"}), 400

    if not password or not is_valid_password(password):
        return jsonify({"msg": "Contraseña invalida"}), 400

    user.email = email
    user.password = hash_password(password, bcrypt)
    user.first_name = first_name
    user.last_name = last_name

    db.session.add(user)
    db.session.commit()

    return jsonify({"msg": "Usuario creado"}), 201
    
@app.route("/transaction/<int:transaction_id>", methods=["PUT", "DELETE"])
def update_transaction(transactions_id):
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
#categoria
@app.route("/categorys", methods=["GET"]) #Read
def get_category():
    type_of_movements = Type_of_movement.query.all()
    type_of_movements = list (map(lambda type_of_movement: type_of_movement.serialize(), type_of_movements))
    return jsonify(type_of_movements)

@app.route("/category", methods=["POST"]) #Create
def category():
    data = request.get_json()
    user = User()
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    email = data.get("email")
    password = data.get("password")

    if not email or not is_valid_email(email):
        return jsonify({"msg": "Correo invalido"}), 400

    if find_user_by_email(email):
        return jsonify({"msg": "El usuario ya existe"}), 400

    if not password or not is_valid_password(password):
        return jsonify({"msg": "Contraseña invalida"}), 400

    user.email = email
    user.password = hash_password(password, bcrypt)
    user.first_name = first_name
    user.last_name = last_name

    db.session.add(user)
    db.session.commit()

    return jsonify({"msg": "Usuario creado"}), 201
    
@app.route("/category/<int:category_id>", methods=["PUT", "DELETE"])
def update_category(category_id):
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

if __name__ == "__main__":
    app.run(host="localhost", port=5050, debug=True)