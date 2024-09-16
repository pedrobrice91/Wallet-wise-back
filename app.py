from flask import Flask, jsonify, request
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from flask_bcrypt import Bcrypt
from models import db, User, Type_of_movement, Transaction, Movement_goal, Movement, Goal, Count, Category
import re

app = Flask(__name__) 
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///wallet-wise.db"
app.config["JWT_SECRET_KEY"] = "secret_key"
app.config["SECRET_KEY"] = "contrasena-super-segura"
JWTManager(app)
bcrypt = Bcrypt(app)
db.init_app(app)
Migrate(app, db)

@app.route("/", methods=["GET"])
def home():
    return "<h1>Hola desde Flask PT 50</h1>"

@app.route("/user", methods=["POST"])
def user():
    data = request.get_json()
    user = User()
    name = data["name"]
    email = data["email"]
    password = data["password"]

    if email is not None:
        email_re = r"^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$"
        if re.match(email_re, email):
            user.email = email
        else:
            return jsonify({
                "msg": "Correo con formato invalido"
            }), 400
    else:
        return jsonify({
            "msg": "El email es requerido"
        }), 400
    
    if password is not None:
        password_re = r"^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}$"
        if re.match(password_re, password):
            password_hash = bcrypt.generate_password_hash(password)
            user.password = password_hash
        else:
            return jsonify({
                "msg": "Formato de contraseña no valido"
            }), 400
    else:
        return jsonify({
            "msg": "La contraseña es requerida"
        }), 400
    
    user.name = name

    db.session.add(user)
    db.session.commit()

    return "Usuario creado"

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