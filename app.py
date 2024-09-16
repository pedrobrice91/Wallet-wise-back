from flask import Flask, jsonify, request
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from flask_bcrypt import Bcrypt
from models import db, User, Type_of_movement, Transaction, Movement_goal, Movement, Goal, Count, Category
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

@app.route("/", methods=["GET"])
def home():
    return "<h1>Hola desde Flask PT 50</h1>"

@app.route("/user", methods=["POST"])
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

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not is_valid_email(email):
        return jsonify({"msg": "Correo invalido"}), 400
    
    user = find_user_by_email(email)
    if user and check_password(user.password, password, bcrypt):
        access_token = create_access_token(identity=email)
        return jsonify({"msg": "Éxito", "access_token": access_token}), 200
    return jsonify({"msg": "Credenciales incorrectas"}), 400

@app.route("/users", methods=["GET"]) #Read
def get_users():
    users = User.query.all()
    users = list(map(lambda user: user.serialize(), users))

    return jsonify(users)

@app.route("/user/<int:user_id>", methods=["PUT", "DELETE"])
def update_user(user_id):
    if request.method == "PUT": #Update
        user = User.query.get(user_id)
        if user is not None:
            data = request.get_json()
            user.name = data["name"]
            if data["password"]:
                return jsonify("No puedes modificar la contraseña"),400

            db.session.commit()
            return jsonify(user.serialize()), 200
        else:
            return jsonify("Usuario no encontrado"), 404
    else:
        user = User.query.get(user_id) #Delete
        if user is not None:
            db.session.delete(user)
            db.session.commit()

            return jsonify("Usuario eliminado"), 201
        else:
            return jsonify("Usuario no encontrado"), 404
        
if __name__ == "__main__":
    app.run(host="localhost", port=5050, debug=True)