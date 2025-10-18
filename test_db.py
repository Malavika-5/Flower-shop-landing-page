from app import app, db
from sqlalchemy import text

with app.app_context():
    print("✅ DB Connection OK ->", db.session.execute(text("SELECT 1")).scalar())
