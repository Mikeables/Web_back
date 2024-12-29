from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(11), unique=True, nullable=False)  # 手机号长度为11位
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), default='user')  # 默认为普通用户

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    product_code = db.Column(db.String(50), unique=True, nullable=False)
    price = db.Column(db.Float, nullable=False)

class Cart(db.Model):
    __tablename__ = 'cart'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, default=1)  # 添加数量字段

class Logistics(db.Model):
    __tablename__ = 'logistics'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    order_id = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    tracking_info = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False) 