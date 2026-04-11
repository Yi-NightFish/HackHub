from app import app, db, User
with app.app_context():
    db.create_all()  # Create tables if they don't exist
    db.session.query(User).delete() 
    user1 = (User(email="hi@gmail.com", password="123", is_verified=True))
    user2 = (User(email="bye@gmail.com", password="456", is_verified=False))
    db.session.add_all([user1, user2])
    db.session.commit()
    print("Seeded successfully")