from app import db

class User(db.Model):  
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(200))
    is_verified = db.Column(db.Boolean, default=False)
    
class OTP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120))
    code = db.Column(db.String(6))
    purpose = db.Column(db.String(20))  
    expiry = db.Column(db.DateTime)