from app import app, db, Product

print("SQLALCHEMY_DATABASE_URI =", app.config['SQLALCHEMY_DATABASE_URI'])

with app.app_context():
    products = [
        {"name": "Classic Roses", "price": 29.99},
        {"name": "Mixed Bouquet", "price": 39.99},
        {"name": "Sunflower Gift", "price": 24.99}
    ]

    for p in products:
        db.session.add(Product(name=p["name"], price=p["price"]))

    db.session.commit()
    print("✅ Seeded 3 products successfully!")
