from flask import Flask, request, render_template, jsonify

app = Flask(__name__)

# Homepage (currently just a test)
@app.route('/')
def home():
    return "Welcome to the Flower Shop Backend!"

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
