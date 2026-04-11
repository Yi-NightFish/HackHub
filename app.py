from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SECRET_KEY"] = "hachhub-key"

#db setup
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
db = SQLAlchemy(app)

class User(db.Model):  #ni my db table
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    
@app.route("/")
def home():
    return "WElcome!"

@app.route("/login", methods = ["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email = email, password = password).first()
        if user:
            return f"Login success -> {email}"
        else:
            return "Invalid email or password"
    return render_template("login.html")

@app.route("/register", methods = ["GET","POST"])
def register(): 
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        # avoid error if same email register more than once
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return "Email already registered"
        
        user = User(email = email, password = password)
        db.session.add(user)
        db.session.commit()
        return redirect("/login")
    return render_template("register.html")

@app.route("/logout")
def logout():
    return "Logged out successfully"

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)