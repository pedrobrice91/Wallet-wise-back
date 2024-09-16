import re
from models import User

# Validar el formato del correo electrónico
def is_valid_email(email):
    email_re = r"^[\w\.-]+@([\w-]+\.)+[\w-]{2,4}$"
    return re.match(email_re, email)

# Validar el formato de la contraseña
def is_valid_password(password):
    password_re = r"^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}$"
    return re.match(password_re, password)

# Buscar un usuario por correo electrónico
def find_user_by_email(email):
    return User.query.filter_by(email=email).first()

# Generar un hash de la contraseña
def hash_password(password, bcrypt):
    return bcrypt.generate_password_hash(password)

# Verificar si la contraseña proporcionada coincide con el hash almacenado
def check_password(user_password, password, bcrypt):
    return bcrypt.check_password_hash(user_password, password)