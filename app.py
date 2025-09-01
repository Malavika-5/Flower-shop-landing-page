from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    products = Product.query.all()
    return render_template('index.html', products=products)

if __name__ == "__main__":
    app.run(debug=True)