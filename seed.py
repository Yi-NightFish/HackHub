from app import app, db, User
with app.app_context():
    db.create_all()  # Create tables if they don't exist
    db.session.query(User).delete() 
    user1 = (User(email="hi@gmail.com", password="123"))
    user2 = (User(email="bye@gmail.com", password="456"))
    db.session.add_all([user1, user2])
    db.session.commit()
    print("Seeded successfully")