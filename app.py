from flask import Flask, request, render_template, jsonify, session

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a strong secret in production

# Homepage
@app.route('/')
def home():
    return render_template('index.html')

# Contact form submission
@app.route('/contact', methods=['POST'])
def contact():
    name = request.form.get('name')
    email = request.form.get('email')
    bouquet = request.form.get('bouquet')
    message = request.form.get('message')

    # For now, just print the data (database integration can be added later)
    print(f"📩 New Contact - Name: {name}, Email: {email}, Bouquet: {bouquet}, Message: {message}")

    return jsonify({"status": "success", "message": "Your message has been received!"})

# Route to serve a catalog page if you want a separate catalog
@app.route('/catalog')
def catalog():
    return render_template('index.html')  # Or a separate catalog.html if you have one

# Route for about page
@app.route('/about')
def about():
    return render_template('index.html')  # Or a separate about.html if you have one

#route for cart

@app.route('/cart')
def cart():
    return render_template('cart.html')

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

#route for order
@app.route('/order', methods=['POST'])
def order():
    data = request.get_json()
    email = data.get('email')
    fullname = data.get('fullname')
    address = data.get('address')
    phone = data.get('phone')
    instructions = data.get('instructions')
    cardname = data.get('cardname')
    cardnumber = data.get('cardnumber')
    expiry = data.get('expiry')
    cvv = data.get('cvv')
    # You can add more fields as needed

    # For now, just print the order (add DB/email logic later)
    print(f"🛒 New Order - Email: {email}, Name: {fullname}, Address: {address}, Phone: {phone}")

    return jsonify({"status": "success", "message": "Order received!"})
    
if __name__ == '__main__':
    app.run(debug=True)

fetch("{{ url_for('submit_order') }}", ...)
