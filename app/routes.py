from flask import render_template, request, url_for, redirect, session
import random
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from flask_mail import Message
import functools

from app import app, db, mail
from app.models import User, OTP
from app.forms import ProfileForm

#By Wan Yi
def send_otp(email, otp):
    msg = Message(
        "HackHub OTP",
        sender=app.config["MAIL_USERNAME"],
        recipients=[email]
    )
    msg.body = f"Your OTP is: {otp}"
    mail.send(msg)
    
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        # Check if the user is logged in
        if "user_id" not in session:
            # If not logged in, redirect them to the login page
            return redirect(url_for("login"))
        # If logged in, proceed to the requested page
        return view(**kwargs)
    return wrapped_view

@app.route("/")
def home():
    return "Welcome!"

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        # check if email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return "Email already registered"
        otp = random.randint(100000, 999999)
        hashed_password = generate_password_hash(password)
        session["temp_email"] = email
        session["temp_password"] = hashed_password

        db.session.add(OTP(email=email, code=otp, purpose="register", expiry=datetime.now() + timedelta(minutes=5)))
        db.session.commit()
        send_otp(email, otp)
        return redirect("/verify-register")
    return render_template("register.html")

@app.route("/verify-register", methods=["GET", "POST"])
def verify_register():
    if request.method == "POST":
        email = session.get("temp_email")
        otp = request.form["otp"]
        record = OTP.query.filter_by(
            email=email,
            code=otp,
            purpose="register"
        ).first()
        if record and record.expiry > datetime.now():
            user = User(
                email=email,
                password=session.get("temp_password"),
                is_verified=True
            )
            db.session.add(user)
            db.session.delete(record)
            db.session.commit()
            session.pop("temp_email", None)
            session.pop("temp_password", None)
            session["user_id"] = user.id
            return redirect("/login")
        return "Invalid OTP"
    return render_template("otp_veri.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = User.query.filter_by(email=email).first()

        #Redefine check_password_hash for testing purposes. Delete this in production and use the one from werkzeug.security.
        def check_password_hash(stored_password, provided_password):
            return stored_password == provided_password

        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            return redirect("/dashboard")
        return "Invalid credentials"
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return "Logged out successfully"

@app.route("/dashboard")
@login_required
def dashboard():
    if "user_id" not in session:
        return redirect("/login")
    user = db.session.get(User, session["user_id"])
    return f"Welcome {user.email} ---> ID: {user.id}"

@app.route("/forget", methods=["GET", "POST"])
def forget():
    if request.method == "POST":
        email = request.form["email"]
        user = User.query.filter_by(email=email).first()
        if not user:
            return "User not found"
        otp = str(random.randint(100000, 999999))
        db.session.add(OTP(
            email=email,
            code=otp,
            purpose="reset",
            expiry=datetime.now() + timedelta(minutes=5)
        ))
        db.session.commit()
        session["reset_email"] = email
        send_otp(email, otp)
        return redirect("/verify-reset")
    return render_template("forget_ps.html")

@app.route("/verify-reset", methods=["GET", "POST"])
def verify_reset():
    if request.method == "POST":
        email = session.get("reset_email")
        otp = request.form["otp"]
        record = OTP.query.filter_by(
            email=email,
            code=otp,
            purpose="reset"
        ).first()
        if record and record.expiry > datetime.now():
            db.session.delete(record)
            db.session.commit()
            session["reset_verified"] = True
            return redirect("/reset-password")
        return "Invalid / Expired OTP"
    return render_template("otp_veri.html")

@app.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    if request.method == "POST":
        if not session.get("reset_verified"):
            return "Not allowed"
        new_password = generate_password_hash(request.form["password"])
        email = session.get("reset_email")
        user = User.query.filter_by(email=email).first()
        user.password = new_password
        db.session.commit()
        return redirect("/login")
    return render_template("reset.html")

# By Soon Hong
@app.route("/profile/<user_id>", methods = ["GET", "POST"])
@login_required
def profile(user_id):
    profile_page = ProfileForm()
    user = db.session.get(User, user_id)
    if user is None:
        return "User not found"
    
    if profile_page.validate_on_submit():
        if user.id != session["user_id"]:
            return "Unauthorized", 403
        user.name = profile_page.username.data
        user.university = profile_page.university.data
        user.skills = profile_page.skills.data
        user.github_link = profile_page.github_link.data
        db.session.commit()
        new_email = profile_page.email.data

        # handle the case where the user updates their email, which requires them to verify the new email address before it takes effect
        # for testing purpose, need to refactor out email verification logic from register and verify_register
        def verify_email():
            otp = random.randint(100000, 999999)
            db.session.add(OTP(email=new_email, code=otp, purpose="update_email", expiry=datetime.now() + timedelta(minutes=5)))
            db.session.commit()

            def send_otp(email, otp):
                print(f"Sending OTP {otp} to {email} for email update verification")

            send_otp(new_email, otp)

        if profile_page.email.data != user.email:
            session["temp_email"] = new_email
            verify_email()
            return redirect("/verify-update-email")

        return redirect(url_for("profile", user_id=user_id))

    return render_template("profile.html", form = profile_page, user = user, current_user = db.session.get(User, session["user_id"]))

@app.route("/reset_pwd")
def reset_pwd():
    pass

# For testing only. Delete after refactoring email verification logic out of register and verify_register.
@app.route("/verify-update-email", methods=["GET", "POST"])
def verify_update_email():
    if request.method == "POST":
        email = session.get("temp_email")
        otp = request.form["otp"]
        record = OTP.query.filter_by(
            email=email,
            code=otp,
            purpose="update_email"
        ).first()
        if record and record.expiry > datetime.now():
            user = db.session.get(User, session["user_id"])
            user.email = email
            db.session.delete(record)
            db.session.commit()
            session.pop("temp_email", None)
            return redirect(url_for("profile", user_id=user.id))
        return "Invalid OTP"
    return render_template("otp_veri.html")
