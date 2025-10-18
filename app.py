from flask import Flask, request, render_template, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a strong secret in production

# Load environment variables from .env
load_dotenv()

DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')

# MySQL connection string
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Debug: show DB URI for troubleshooting (remove in production)
print("SQLALCHEMY_DATABASE_URI=", app.config.get('SQLALCHEMY_DATABASE_URI'))
db = SQLAlchemy(app)


class Product(db.Model):  # Renamed from Flower to Product
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    # added price to avoid template errors
    price = db.Column(db.Float, nullable=True)


class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(300))
    phone = db.Column(db.String(30))
    instructions = db.Column(db.String(500))
    cardname = db.Column(db.String(120))
    # avoid storing raw card data in production
    cardnumber = db.Column(db.String(64))
    expiry = db.Column(db.String(20))
    cvv = db.Column(db.String(10))
    items = db.Column(db.Text)
    total = db.Column(db.Float)
    created_at = db.Column(db.DateTime, server_default=db.func.now())


class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey(
        'product.id'), nullable=False)  # changed
    quantity = db.Column(db.Integer, nullable=False)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)


class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    message = db.Column(db.Text)


class Order(db.Model):
    __tablename__ = 'orders'  # instead of 'order'


# Homepage


@app.route('/')
def home():
    return render_template('index.html')

# Cart page


@app.route('/cart')
def cart():
    cart_items = session.get('cart', [])
    cart_total = sum(float(item['price']) * item.get('qty', 1)
                     for item in cart_items) if cart_items else 0
    no_cart_items = len(cart_items) == 0
    return render_template('cart.html', cart_items=cart_items, cart_total=cart_total, no_cart_items=no_cart_items)

# Order page (GET)


@app.route('/order')
def order_page():
    cart_items = session.get('cart', [])
    subtotal = sum((float(item.get('price', 0)) * int(item.get('qty', 1)))
                   for item in cart_items)
    delivery_fee = 0.0
    tax = 0.0
    total = subtotal + delivery_fee + tax
    return render_template('order.html',
                           cart_items=cart_items,
                           subtotal=subtotal,
                           delivery_fee=delivery_fee,
                           tax=tax,
                           total=total)

# Contact form submission


@app.route('/contact', methods=['POST'])
def contact():
    name = request.form.get('name')
    email = request.form.get('email')
    bouquet = request.form.get('bouquet')
    message = request.form.get('message')
    print(
        f"📩 New Contact - Name: {name}, Email: {email}, Bouquet: {bouquet}, Message: {message}")
    return jsonify({"status": "success", "message": "Your message has been received!"})

# Catalog page


@app.route('/catalog')
def catalog():
    # Change to catalog.html if you have one
    return render_template('index.html')

# About page


@app.route('/about')
def about():
    # Change to about.html if you have one
    return render_template('index.html')

# Cart API routes


@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    data = request.get_json() or request.form or {}
    # accept either product_id or id, and qty or quantity
    product_id = data.get('product_id') or data.get('id')
    try:
        qty = int(data.get('qty') or data.get('quantity') or 1)
    except (TypeError, ValueError):
        qty = 1

    cart = session.get('cart', [])

    # normalize existing ids to string for reliable comparison
    found = False
    for item in cart:
        if str(item.get('id')) == str(product_id):
            item['qty'] = int(item.get('qty', 1)) + qty
            found = True
            break

    if not found:
        product = {
            'id': product_id,
            'name': data.get('name') or data.get('title') or 'Product',
            'price': data.get('price') or data.get('unit_price') or 0,
            'label': data.get('label'),
            'qty': qty,
            'image': data.get('image')
        }
        cart.append(product)

    session['cart'] = cart
    session.modified = True

    # debug log — remove in production
    print("ADD_TO_CART payload:", data)
    print("CURRENT CART:", cart)

    return jsonify({"status": "success", "cart": cart})


@app.route('/update_cart_qty', methods=['POST'])
def update_cart_qty():
    data = request.get_json()
    product_id = data.get('product_id')
    qty = int(data.get('qty', 1))
    if 'cart' in session:
        for item in session['cart']:
            if str(item['id']) == str(product_id):
                item['qty'] = qty
                break
        session.modified = True
    return jsonify({"status": "success", "cart": session['cart']})


@app.route('/cart/items', methods=['GET'])
def get_cart_items():
    return jsonify(session.get('cart', []))


@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    data = request.get_json()
    product_id = data.get('product_id')
    cart = session.get('cart', [])
    session['cart'] = [item for item in cart if str(
        item['id']) != str(product_id)]
    session.modified = True
    return jsonify({"status": "success", "cart": session['cart']})


@app.route('/clear_cart', methods=['POST'])
def clear_cart():
    session['cart'] = []
    session.modified = True
    return jsonify({"status": "success"})

# Order submission (POST)


# ...existing code...
@app.route('/order', methods=['POST'])
def submit_order():
    data = request.get_json() or {}
    # minimal: save order record (requires db.create_all run earlier)
    order = Order(
        fullname=data.get('fullname'),
        email=data.get('email'),
        address=data.get('address'),
        phone=data.get('phone'),
        items=str(session.get('cart', [])),
        total=data.get('total', 0)
    )
    db.session.add(order)
    db.session.commit()
    session['cart'] = []
    return jsonify({"status": "success", "message": "Order received"})


if __name__ == '__main__':
    with app.app_context():   # Required for SQLAlchemy to know app context
        db.create_all()
    app.run(debug=True)
