from flask import Flask, request, render_template, jsonify

app = Flask(__name__)

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

if __name__ == '__main__':
    app.run(debug=True)
