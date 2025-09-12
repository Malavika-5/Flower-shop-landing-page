from flask import Flask, request, render_template, jsonify, session

app = Flask(__name__)
app.secret_key = 'your_secret_key'
# Homepage (currently just a test)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    data = request.get_json()
    product_id = data.get('product_id')
    # Initialize cart in session if not present
    if 'cart' not in session:
        session['cart'] = []
    session['cart'].append(product_id)
    session.modified = True
    return jsonify({'status': 'success'})


@app.route('/cart')
def cart():
    cart_items = session.get('cart', [])
    cart_total = sum(float(item['price']) * item.get('qty', 1)
                     for item in cart_items) if cart_items else 0
    no_cart_items = len(cart_items) == 0
    return render_template('cart.html', cart_items=cart_items, cart_total=cart_total, no_cart_items=no_cart_items)


@app.route('/order')
def order():
    return render_template('order.html')


# Contact form submission


@app.route('/contact', methods=['POST'])
def contact():
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')

    # For now just print it (later store in DB)
    print(f"📩 New Contact - Name: {name}, Email: {email}, Message: {message}")

    return jsonify({"status": "success", "message": "Your message has been received!"})


if __name__ == '__main__':
    app.run(debug=True)
