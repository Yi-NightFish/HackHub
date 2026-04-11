from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from itsdangerous import URLSafeTimedSerializer

app = Flask(__name__)
app.config["SECRET_KEY"] = "hachhub-key"
#db setup
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
db = SQLAlchemy(app)

def generate_verification_token(email):
    serializer = URLSafeTimedSerializer(app.config["SECRET_KEY"])
    return serializer.dumps(email, salt="email-confirm")
def confirm_verification_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(app.config["SECRET_KEY"])
    try:
        email = serializer.loads(
            token,
            salt="email-confirm",
            max_age=expiration
        )
        return email
    except Exception:
        return None
class User(db.Model):  #ni my db table
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    
@app.route("/")
def home():
    return "WElcome!"

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        # check if email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return "Email already registered"

        user = User(email=email, password=password, is_verified=False)
        db.session.add(user)
        db.session.commit()
        # simple verification
        token = generate_verification_token(user.email)
        verify_link = url_for("verify_email", token=token, _external=True)
        return f"Registered successfully. Verify your email here: {verify_link}"
    return render_template("register.html")

@app.route("/verify-email/<token>")
def verify_email(token):
    email = confirm_verification_token(token)
    if not email:
        return "Invalid or expired verification link"
    user = User.query.filter_by(email=email).first()
    if not user:
        return "User not found"
    user.is_verified = True
    db.session.commit()
    return "Email verified successfully. You can now log in."

@app.route("/login", methods = ["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email = email, password = password).first()
        if user and user.is_verified:
            return f"Login success -> {email}"
        if user and not user.is_verified:
            return "Please verify your email before logging in"
        else:
            return "Invalid email or password"
        
    return render_template("login.html")

@app.route("/logout")
def logout():
    return "Logged out successfully"

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)