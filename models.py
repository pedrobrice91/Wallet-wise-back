from flask_sqlalchemy import SQLAlchemy
import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    email = db.Column(db.String(200), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now())
    count = db.relationship("count")

class Count(db.Model):
    __tablename__ = "count"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.datetime.now())
    user_id = db.Column(db.Integer, db.foreignkey("user.id"))
    goal = db.relationship("goal")
    movement = db.relationship("movement")

class Goal(db.Model):
    __tablename__ = "goal"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    fulfillment_amount = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.datetime.now())
    estimated_monthly = db.Column(db.String(200))
    monthly_contribution = db.Column(db.DateTime, default=datetime.datetime.now())
    count_id = db.Column(db.Integer, db.foreignkey("count.id"))
    movement_goal = db.relationship("movement_goal")

class Movement(db.Model):
    __tablename__ = "movement"
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(200))
    transaccion = db.Column(db.String(200))
    amount = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now())
    count_id = db.Column(db.Integer, db.foreignkey("count.id"))
    movement_goal = db.relationship("movement_goal")

class Movement_goal(db.Model):
    __tablename__ = "movement_goal"
    id = db.Column(db.Integer, primary_key=True)
    goal_id = db.Column(db.Integer, db.foreignkey("goal_id"))
    movement_id = db.Column(db.Integer, db.foreignkey("movement_id"))

class Transaction(db.Model):
    __tablename__ = "transaction"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    category_id = db.relationship("category_id")

class Category(db.Model):
    __tablename__ = "category"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    type_of_movement_id = db.Column(db.Integer, db.foreignkey("type_of_movement_id"))
    category_id = db.relationship("category_id")

class Type_of_movement(db.Model):
    __tablename__ = "type_of_movement"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    category = db.relationship("category")
