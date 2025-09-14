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
    qty = int(data.get('qty', 1))
    if 'cart' not in session:
        session['cart'] = []
    # Check if product already in cart
    for item in session['cart']:
        if str(item['id']) == str(product_id):
            item['qty'] += qty
            break
    else:
        product = {
            'id': product_id,
            'name': data.get('name'),
            'price': data.get('price'),
            'label': data.get('label'),
            'qty': qty,
            'image': data.get('image')
        }
        session['cart'].append(product)
    session.modified = True
    return jsonify({'status': 'success'})


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
    return jsonify({'status': 'success'})


@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    data = request.get_json()
    product_id = data.get('product_id')
    if 'cart' in session:
        session['cart'] = [item for item in session['cart']
                           if str(item['id']) != str(product_id)]
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
    cart_items = session.get('cart', [])
    delivery_fee = 10.00
    subtotal = sum(float(item['price']) * item.get('qty', 1)
                   for item in cart_items)
    tax = round(subtotal * 0.09, 2)
    total = round(subtotal + delivery_fee + tax, 2)
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
    message = request.form.get('message')

    # For now just print it (later store in DB)
    print(f"📩 New Contact - Name: {name}, Email: {email}, Message: {message}")

    return jsonify({"status": "success", "message": "Your message has been received!"})


if __name__ == '__main__':
    app.run(debug=True)
