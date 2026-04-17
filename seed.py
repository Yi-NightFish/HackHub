from app import app, db, User
from werkzeug.security import generate_password_hash
with app.app_context():
    db.drop_all()  # Drop all tables to start fresh
    db.create_all()  # Create tables if they don't exist
    # db.session.query(User).delete() 
    user1 = (User(email="hi@gmail.com", password="123", is_verified=True))
    user2 = (User(email="bye@gmail.com", password="456", is_verified=False))
    me = (User(email="tanwanyi007@gmail.com", password="789", is_verified=True))
    db.session.add_all([user1, user2, me])
    db.session.commit()
    print("Seeded successfully")