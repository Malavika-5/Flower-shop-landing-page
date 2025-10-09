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

db = SQLAlchemy(app)

class Product(db.Model):  # Renamed from Flower to Product
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    instructions = db.Column(db.String(300))
    cardname = db.Column(db.String(100))
    cardnumber = db.Column(db.String(20))
    expiry = db.Column(db.String(10))
    cvv = db.Column(db.String(10))
    items = db.Column(db.Text)  # Store cart items as JSON string
    total = db.Column(db.Float)

# Homepage
@app.route('/')
def home():
    return render_template('index.html')

# Cart page
@app.route('/cart')
def cart():
    return render_template('cart.html')

# Order page (GET)
@app.route('/order')
def order():
    return render_template('order.html')

# Contact form submission
@app.route('/contact', methods=['POST'])
def contact():
    name = request.form.get('name')
    email = request.form.get('email')
    bouquet = request.form.get('bouquet')
    message = request.form.get('message')
    print(f"📩 New Contact - Name: {name}, Email: {email}, Bouquet: {bouquet}, Message: {message}")
    return jsonify({"status": "success", "message": "Your message has been received!"})

# Catalog page
@app.route('/catalog')
def catalog():
    return render_template('index.html')  # Change to catalog.html if you have one

# About page
@app.route('/about')
def about():
    return render_template('index.html')  # Change to about.html if you have one

# Cart API routes
@app.route('/cart/add', methods=['POST'])
def add_to_cart():
    item = request.get_json()
    cart = session.get('cart', [])
    cart.append(item)
    session['cart'] = cart
    return jsonify({"status": "success", "message": "Item added to cart!", "cart": cart})

@app.route('/cart/items', methods=['GET'])
def view_cart():
    cart = session.get('cart', [])
    return jsonify(cart)

@app.route('/cart/remove', methods=['POST'])
def remove_from_cart():
    index = request.get_json().get('index')
    cart = session.get('cart', [])
    if 0 <= index < len(cart):
        removed = cart.pop(index)
        session['cart'] = cart
        return jsonify({"status": "success", "message": "Item removed", "removed": removed, "cart": cart})
    return jsonify({"status": "error", "message": "Invalid index"}), 400

@app.route('/cart/clear', methods=['POST'])
def clear_cart():
    session['cart'] = []
    return jsonify({"status": "success", "message": "Cart cleared"})

# Order submission (POST)
@app.route('/order', methods=['POST'])
def submit_order():
    data = request.get_json()
    order = Order(
        fullname=data.get('fullname'),
        email=data.get('email'),
        address=data.get('address'),
        phone=data.get('phone'),
        instructions=data.get('instructions'),
        cardname=data.get('cardname'),
        cardnumber=data.get('cardnumber'),
        expiry=data.get('expiry'),
        cvv=data.get('cvv'),
        items=str(session.get('cart', [])),
        total=data.get('total', 0)
    )
    db.session.add(order)
    db.session.commit()
    session['cart'] = []
    return jsonify({"status": "success", "message": "Order received!"})

if __name__ == '__main__':
    app.run(debug=True)
