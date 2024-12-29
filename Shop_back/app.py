from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from models import db, User, Product, Cart, Logistics
import config
from datetime import datetime
import random  # 新增：用于生成随机订单号
import json
from flask_cors import CORS

# 先定义函数
def add_sample_products():
    products = [
        {"name": "iPhone 15 Pro", "type": "手机", "product_code": "IP15P", "price": 8999.00},
        {"name": "MacBook Pro 14", "type": "笔记本", "product_code": "MBP14", "price": 14999.00},
        {"name": "AirPods Pro", "type": "耳机", "product_code": "APP2", "price": 1999.00},
        {"name": "iPad Air", "type": "平板", "product_code": "IPA5", "price": 4799.00},
        {"name": "Nike Air Max", "type": "运动鞋", "product_code": "NAM1", "price": 899.00},
        {"name": "Adidas Ultra Boost", "type": "运动鞋", "product_code": "AUB1", "price": 1299.00},
        {"name": "索尼 WH-1000XM4", "type": "耳机", "product_code": "SWH4", "price": 2299.00},
        {"name": "华为 Mate 60 Pro", "type": "手机", "product_code": "HM60P", "price": 6999.00},
        {"name": "联想 YOGA", "type": "笔记本", "product_code": "LY14", "price": 5999.00},
        {"name": "戴尔 XPS 13", "type": "笔记本", "product_code": "DX13", "price": 9999.00},
        {"name": "三星 Galaxy S24", "type": "手机", "product_code": "SGS24", "price": 7999.00},
        {"name": "小米手环 8", "type": "智能手环", "product_code": "XM8", "price": 249.00},
        {"name": "华为手表 GT4", "type": "智能手表", "product_code": "HGT4", "price": 1599.00},
        {"name": "罗技 MX Master 3", "type": "鼠标", "product_code": "LMX3", "price": 699.00},
        {"name": "机械键盘 K2", "type": "键盘", "product_code": "MKK2", "price": 499.00},
        {"name": "显示器 4K", "type": "显示器", "product_code": "M4K", "price": 2499.00},
        {"name": "游戏主机 PS5", "type": "游戏机", "product_code": "PS5", "price": 3899.00},
        {"name": "Nintendo Switch", "type": "游戏机", "product_code": "NS", "price": 2099.00},
        {"name": "智能音箱", "type": "音箱", "product_code": "SM1", "price": 299.00},
        {"name": "投影仪 4K", "type": "投影仪", "product_code": "PJ4K", "price": 4999.00}
    ]
    
    for product in products:
        if not Product.query.filter_by(product_code=product["product_code"]).first():
            new_product = Product(
                name=product["name"],
                type=product["type"],
                product_code=product["product_code"],
                price=product["price"]
            )
            db.session.add(new_product)
    db.session.commit()

# 然后初始化应用
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})
app.config.from_object(config)
db.init_app(app)

# 创建所有数据库表
with app.app_context():
    db.create_all()
    add_sample_products()

@app.route('/api/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify([{
        'id': product.id,
        'name': product.name,
        'type': product.type,
        'product_code': product.product_code,
        'price': product.price
    } for product in products])

@app.route('/api/user/register', methods=['POST'])
def register():
    try:
        data = request.json
        # 验证手机号格式
        username = data.get('username', '')
        if not username.isdigit() or len(username) != 11:
            return jsonify({'message': '请输入有效的11位手机号'}), 400
        
        # 检查手机号是否已注册
        if User.query.filter_by(username=username).first():
            return jsonify({'message': '该手机号已注册'}), 400
        
        # 验证密码
        password = data.get('password', '')
        if len(password) < 6 or len(password) > 20:
            return jsonify({'message': '密码长度应在6-20位之间'}), 400
        
        # 创建新用户
        new_user = User(
            username=username,
            password=password,
            role='user'  # 默认为普通用户
        )
        
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': '注册成功'}), 201
    except Exception as e:
        db.session.rollback()
        print("Registration error:", str(e))
        return jsonify({'message': '注册失败，请稍后重试'}), 500

@app.route('/api/user/login', methods=['POST'])
def login():
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({'message': '请输入用户名和密码'}), 400

        user = User.query.filter_by(username=username).first()
        
        if user and user.password == password:
            return jsonify({
                'message': '登录成功',
                'data': {
                    'id': user.id,
                    'username': user.username,
                    'role': user.role
                }
            }), 200
        else:
            return jsonify({'message': '手机号或密码错误'}), 401
            
    except Exception as e:
        print("Login error:", str(e))
        return jsonify({'message': '登录失败，请稍后重试'}), 500

@app.route('/api/cart/<int:user_id>', methods=['GET'])
def get_cart(user_id):
    cart_items = Cart.query.filter_by(user_id=user_id).all()
    return jsonify([{
        'id': item.id,
        'product_name': item.product_name,
        'price': item.price,
        'quantity': item.quantity
    } for item in cart_items])

@app.route('/api/cart', methods=['POST'])
def add_to_cart():
    data = request.json
    new_cart_item = Cart(
        user_id=data['user_id'],
        product_name=data['product_name'],
        price=data['price'],
        quantity=data['quantity']
    )
    db.session.add(new_cart_item)
    db.session.commit()
    return jsonify({'message': '添加成功'}), 201

@app.route('/api/cart/<int:cart_id>', methods=['DELETE'])
def delete_from_cart(cart_id):
    cart_item = Cart.query.get(cart_id)
    if cart_item:
        db.session.delete(cart_item)
        db.session.commit()
        return jsonify({'message': '删除成功'}), 200
    return jsonify({'message': '商品不存在'}), 404

@app.route('/api/logistics', methods=['POST'])
def create_order():
    try:
        # 获取前端传来的订单数据
        data = request.json
        
        # 生成订单号（时间戳+用户ID+随机数）
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        random_num = ''.join(random.choices('0123456789', k=6))
        order_id = f"{timestamp}{data['user_id']}{random_num}"
        
        # 创建新的物流订单实例
        new_logistics = Logistics(
            user_id=data['user_id'],
            order_id=order_id,
            status='待发货',  # 初始状态
            tracking_info=json.dumps({
                'receiver': data['receiver'],
                'phone': data['phone'],
                'address': data['address'],
                'items': data['items']  # 商品列表
            }),
            created_at=datetime.now()
        )
        
        # 添加到数据库会话
        db.session.add(new_logistics)
        
        # 清空用户购物车中已购买的商品
        if 'items' in data:
            for item in data['items']:
                cart_items = Cart.query.filter_by(
                    user_id=data['user_id'],
                    product_name=item['product_name']
                ).all()
                for cart_item in cart_items:
                    db.session.delete(cart_item)
        
        # 提交事务
        db.session.commit()
        
        return jsonify({
            'message': '订单创建成功',
            'order_id': order_id
        }), 201
        
    except Exception as e:
        # 发生错误时回滚事务
        db.session.rollback()
        print("Error creating order:", str(e))
        return jsonify({'message': '订单创建失败，请稍后重试'}), 500

@app.route('/api/logistics/user/<int:user_id>', methods=['GET'])
def get_logistics(user_id):
    logistics = Logistics.query.filter_by(user_id=user_id).all()
    return jsonify([{
        'id': log.id,
        'order_id': log.order_id,
        'status': log.status,
        'tracking_info': log.tracking_info,
        'created_at': log.created_at
    } for log in logistics])

@app.route('/api/logistics/<string:order_id>', methods=['GET'])
def get_logistics_detail(order_id):
    log = Logistics.query.filter_by(order_id=order_id).first()
    if log:
        return jsonify({
            'id': log.id,
            'order_id': log.order_id,
            'status': log.status,
            'tracking_info': log.tracking_info,
            'created_at': log.created_at
        })
    return jsonify({'message': '订单不存在'}), 404

@app.route('/api/logistics/<string:order_id>', methods=['DELETE'])
def delete_order(order_id):
    log = Logistics.query.filter_by(order_id=order_id).first()
    if log:
        db.session.delete(log)
        db.session.commit()
        return jsonify({'message': '订单取消成功'}), 200
    return jsonify({'message': '订单不存在'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)