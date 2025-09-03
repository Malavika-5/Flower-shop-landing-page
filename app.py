from flask import Flask, request, render_template, jsonify

app = Flask(__name__)

# Homepage (currently just a test)
@app.route('/')
def home():
    return render_template('index.html')


@app.route('/cart')
def cart():
    return render_template('cart.html')


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

    # For now, just print the data (database integration can be added later)
    print(f"📩 New Contact - Name: {name}, Email: {email}, Bouquet: {bouquet}, Message: {message}")

    return jsonify({"status": "success", "message": "Your message has been received!"})

if __name__ == '__main__':
    app.run(debug=True)
