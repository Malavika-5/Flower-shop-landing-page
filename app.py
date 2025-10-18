from flask import Flask, request, render_template, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
import sys

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET', 'dev_secret_key')

DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')

if DB_USER and DB_PASSWORD and DB_HOST and DB_NAME:
    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flowershop_dev.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

print("SQLALCHEMY_DATABASE_URI=", app.config.get('SQLALCHEMY_DATABASE_URI'))

db = SQLAlchemy(app)

# Models


class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=True)
    image = db.Column(db.String(200), nullable=True)


class Customer(db.Model):
    __tablename__ = 'customer'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=True)
    email = db.Column(db.String(200), unique=True, nullable=True)
    address = db.Column(db.String(400), nullable=True)
    phone = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())


class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey(
        'customer.id'), nullable=False)
    total_price = db.Column(db.Float, nullable=False, default=0.0)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    customer = db.relationship(
        'Customer', backref=db.backref('orders', lazy=True))


class OrderItem(db.Model):
    __tablename__ = 'order_item'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey(
        'orders.id'), nullable=False)
    product_id = db.Column(
        db.Integer, db.ForeignKey('product.id'), nullable=True)
    product_name = db.Column(db.String(300))
    price = db.Column(db.Float, nullable=True)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    order = db.relationship('Order', backref=db.backref('items', lazy=True))
    product = db.relationship('Product')

# Routes (keep/adjust as needed)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/catalog')
def catalog():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('index.html')


@app.route('/cart')
def cart():
    cart_items = session.get('cart', [])
    cart_total = sum(float(item.get('price', 0)) * int(item.get('qty', 1))
                     for item in cart_items) if cart_items else 0
    no_cart_items = len(cart_items) == 0
    return render_template('cart.html', cart_items=cart_items, cart_total=cart_total, no_cart_items=no_cart_items)


@app.route('/order')
def order_page():
    cart_items = session.get('cart', [])
    subtotal = sum((float(item.get('price', 0)) * int(item.get('qty', 1)))
                   for item in cart_items)
    delivery_fee = 0.0
    tax = 0.0
    total = subtotal + delivery_fee + tax
    return render_template('order.html', cart_items=cart_items, subtotal=subtotal, delivery_fee=delivery_fee, tax=tax, total=total)


@app.route('/contact', methods=['POST'])
def contact():
    # route left for compatibility; contact table removed
    name = request.form.get('name')
    email = request.form.get('email')
    bouquet = request.form.get('bouquet')
    message = request.form.get('message')
    print(
        f"📩 New Contact - Name: {name}, Email: {email}, Bouquet: {bouquet}, Message: {message}")
    return jsonify({"status": "success", "message": "Your message has been received!"})

# Cart API


@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    data = request.get_json() or request.form or {}
    product_id = data.get('product_id') or data.get('id')
    try:
        qty = int(data.get('qty') or data.get('quantity') or 1)
    except (TypeError, ValueError):
        qty = 1
    cart = session.get('cart', [])
    found = False
    for item in cart:
        if str(item.get('id')) == str(product_id):
            item['qty'] = int(item.get('qty', 1)) + qty
            found = True
            break
    if not found:
        try:
            price = float(data.get('price') or 0)
        except (TypeError, ValueError):
            price = 0.0
        product = {'id': product_id, 'name': data.get('name') or data.get(
            'title') or 'Product', 'price': price, 'label': data.get('label'), 'qty': qty, 'image': data.get('image')}
        cart.append(product)
    session['cart'] = cart
    session.modified = True
    print("ADD_TO_CART payload:", data)
    print("CURRENT CART:", cart)
    return jsonify({"status": "success", "cart": cart})


@app.route('/update_cart_qty', methods=['POST'])
def update_cart_qty():
    data = request.get_json() or {}
    product_id = data.get('product_id') or data.get('id')
    try:
        qty = int(data.get('qty', 1))
    except (TypeError, ValueError):
        qty = 1
    cart = session.get('cart', [])
    for item in cart:
        if str(item.get('id')) == str(product_id):
            item['qty'] = qty
            break
    session['cart'] = cart
    session.modified = True
    return jsonify({"status": "success", "cart": cart})


@app.route('/cart/items', methods=['GET'])
def get_cart_items():
    return jsonify(session.get('cart', []))


@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    data = request.get_json() or {}
    product_id = data.get('product_id') or data.get('id')
    cart = session.get('cart', [])
    cart = [item for item in cart if str(item.get('id')) != str(product_id)]
    session['cart'] = cart
    session.modified = True
    return jsonify({"status": "success", "cart": cart})


@app.route('/clear_cart', methods=['POST'])
def clear_cart():
    session['cart'] = []
    session.modified = True
    return jsonify({"status": "success"})


# ...existing code...
@app.route('/order', methods=['POST'])
def submit_order():
    data = request.get_json() or {}
    customer_name = data.get('fullname') or data.get('name') or 'Guest'
    customer_email = data.get('email') or ''
    customer_address = data.get('address') or ''
    customer_phone = data.get('phone') or ''

    # Compute total from session cart (preferred)
    cart = session.get('cart', []) or []
    computed_total = 0.0
    try:
        computed_total = round(sum(
            float(item.get('price', 0)) * int(item.get('qty', 1)) for item in cart
        ), 2)
    except Exception:
        # safe fallback
        computed_total = 0.0

    # If cart is empty and frontend provided a total, use it as fallback
    if computed_total == 0.0:
        try:
            provided = data.get('total')
            if provided is not None and provided != '':
                computed_total = round(float(provided), 2)
        except Exception:
            computed_total = 0.0

    # create/find customer
    customer = None
    if customer_email:
        customer = Customer.query.filter_by(email=customer_email).first()
    if customer:
        customer.name = customer_name
        customer.address = customer_address
        customer.phone = customer_phone
    else:
        unique_email = customer_email or f'guest-{os.urandom(6).hex()}@example.local'
        customer = Customer(name=customer_name, email=unique_email,
                            address=customer_address, phone=customer_phone)
        db.session.add(customer)

    try:
        db.session.flush()
        # save order with computed total
        order = Order(customer_id=customer.id, total_price=computed_total)
        db.session.add(order)
        db.session.flush()

        for it in cart:
            oi = OrderItem(
                order_id=order.id,
                product_id=it.get('id'),
                product_name=it.get('name'),
                price=float(it.get('price') or 0),
                quantity=int(it.get('qty') or 1)
            )
            db.session.add(oi)

        db.session.commit()
        session['cart'] = []
        session.modified = True

        # debug output
        print("ORDER SAVED:", {"order_id": order.id,
              "total": computed_total, "cart": cart})

        return jsonify({"status": "success", "message": "Order received", "order_id": order.id})
    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc(file=sys.stderr)
        return jsonify({"status": "error", "message": "Server error saving order", "detail": str(e)}), 500
# ...existing code...


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
