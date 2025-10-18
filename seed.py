from app import app, db, Product
import sys

print("Using SQLALCHEMY_DATABASE_URI =",
      app.config.get('SQLALCHEMY_DATABASE_URI'))

with app.app_context():
    # Ensure tables exist
    db.create_all()

    # Check current count
    before = Product.query.count()
    print("Products before seeding:", before)

    # Seed only if empty
    if before == 0:
        products = [
            {"name": "Eternal Blush", "price": 80.00},
            {"name": "Bohemian Rhapsody", "price": 75.00},
            {"name": "Summer Solstice", "price": 75.00},
            {"name": "Cotton Candy Dream", "price": 72.00},
            {"name": "Pearl Symphony", "price": 72.00},
            {"name": "Confetti Blooms", "price": 72.00}

        ]
        for p in products:
            db.session.add(Product(name=p["name"], price=p["price"]))
        db.session.commit()
        print("✅ Seeded products.")
    else:
        print("Skipping seed; products already exist.")

    # Print rows to verify
    for prod in Product.query.all():
        print(prod.id, prod.name, prod.price)

    # final count
    print("Products after seeding:", Product.query.count())
