from flask import render_template, request, url_for, redirect, session
import random
from werkzeug.security import generate_password_hash, check_password_hash
import datetime as dt
from flask_mail import Message
import functools

from app import app, db, mail
from app.models import *
from app.forms import ProfileForm
from sqlalchemy import select

#By Wan Yi
# Helper functions
def send_otp(email, purpose):
    otp = str(random.randint(100000, 999999))
    db.session.add(
        OTP(
            email=email,
            code=otp,
            purpose=purpose,
            expiry=dt.datetime.now() + dt.timedelta(minutes=5)
        )
    )
    db.session.commit()
    # msg = Message(
    #     "HackHub OTP",
    #     sender=app.config["MAIL_USERNAME"],
    #     recipients=[email]
    # )
    # msg.body = f"Your OTP is: {otp}"
    # mail.send(msg)

    # Use this to get otp without actually sending to email during development
    print(f"Sent OTP: {otp} -> {email}")
    
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

def verify_otp(purpose, session_key):
    email = session.get(session_key)
    if not email:
        return False
    otp = request.form["otp"]
    otp_record = OTP.query.filter_by(
        email=email,
        code=otp,
        purpose=purpose
    ).first()
    if otp_record and otp_record.expiry > dt.datetime.now():
        db.session.delete(otp_record)
        db.session.commit()
        return True
    return False

# Main routes
@app.route("/")
def home():
    return render_template("home.html", current_user = db.session.get(User, session["user_id"]) if session.get("user_id", None) else None)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        # check if email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return "Email already registered"
        hashed_password = generate_password_hash(password)
        session["temp_email"] = email
        session["temp_password"] = hashed_password
        send_otp(email, purpose = "register")
        return redirect(url_for("verify_register"))
    return render_template("register.html")

@app.route("/verify-register", methods=["GET", "POST"])
def verify_register():
    email = session.get("temp_email", None)
    if request.method == "POST":
        if verify_otp("register", "temp_email"):
            password = session.get("temp_password", None)
            user = User(email = email, 
                        password = password, 
                        is_verified = True, 
            )
            db.session.add(user)
            db.session.commit()
            session.pop("temp_email", None)
            session.pop("temp_password", None)
            return redirect(url_for("login"))    
        return "Invalid OTP"
    return render_template("otp_veri.html",  email = email)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            return redirect("/dashboard")
        return "Invalid credentials"
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

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
        session["reset_email"] = email
        send_otp(email, purpose = "reset")
        return redirect("/verify-reset")
    return render_template("forget_ps.html")

@app.route("/verify-reset", methods=["GET", "POST"])
def verify_reset():
    if request.method == "POST":
        if verify_otp("reset", "reset_email"):
            session["reset_verified"] = True
            return redirect("/reset-password")
        return "Invalid / Expired OTP"
    return render_template("otp_veri.html")

@app.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    user_id = session.get("user_id")
    if user_id:
        # Logged-in user
        user = db.session.get(User, user_id)
        if request.method == "POST":
            current_password = request.form.get("current_password")
            new_password = request.form.get("new_password")
            if not check_password_hash(user.password, current_password):
                return "Incorrect current password"
            user.password = generate_password_hash(new_password)
            db.session.commit()
            return redirect(url_for("profile", user_id=user_id))
        # Show form with current password field
        return render_template("reset.html", logged_in=True)
    else:
        # Email reset
        if not session.get("reset_verified"):
            return "Not allowed"
        if request.method == "POST":
            new_password = request.form.get("new_password")
            email = session.get("reset_email")
            user = User.query.filter_by(email=email).first()
            user.password = generate_password_hash(new_password)
            db.session.commit()
            session.pop("reset_email", None)
            session.pop("reset_verified", None)
            return redirect(url_for("login"))
        # Show form without current password
        return render_template("reset.html", logged_in=False)

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

        if new_email != user.email:
            send_otp(new_email, purpose = "update_email")
            session["new_email"] = new_email
            return redirect(url_for("verify_update_email"))
        return redirect(url_for("profile", user_id=user_id))

    team_member_subquery = select(TeamMember.team_id).where(TeamMember.user_id == user_id).subquery()
    is_team_members_of = db.session.query(Team.event_id).join(team_member_subquery, Team.id == team_member_subquery.c.team_id).subquery()
    events = db.session.execute(db.session.query(Event).join(is_team_members_of, is_team_members_of.c.event_id == Event.id)).scalars().all()
    return render_template("profile.html", 
                           form = profile_page, 
                           user = user, 
                           current_user = db.session.get(User, session["user_id"]),
                           events = events
    )

@app.route("/reset_pwd")
@login_required
def reset_pwd():
    # For logged-in users, allow direct reset without OTP
    return redirect(url_for("reset_password"))

@app.route("/verify-update-email", methods=["GET", "POST"])
@login_required
def verify_update_email():
    new_email = session.get("new_email")
    if request.method == "POST":
        if verify_otp(purpose = "update_email", session_key = "new_email"):
            user = User.query.get(session.get("user_id"))
            user.email = new_email
            db.session.add(user)
            db.session.commit()
            session.pop("new_email")
            return redirect(url_for("profile", user_id = user.id))
        return "Invalid OTP"
    return render_template("otp_veri.html", email = new_email)

from flask import render_template, request, redirect, url_for
from app import db
from app.models import Messages
# from datetime import datetime

def chat_routes(app):
    @app.route("/")
    def chat():
        current_user_id = request.args.get("user_id", 1, type=int)  #user_id=1
        messages = Messages.query.order_by(Messages.timestamp.asc()).all()  #取数据from旧到新
        return render_template("chat.html", messages=messages, current_user_id=current_user_id)
    
    @app.route("/send_message", methods=["POST"])
    def send_message():
        message = request.form["message"]
        sender_id = request.form.get("user_id", type=int)
        receiver_id = 2 if sender_id == 1 else 1  #user1/2互发消息
        new_message = Messages(message=message, sender_id=sender_id, receiver_id=receiver_id) #timestamp会自动生成/存数据库
        db.session.add(new_message)
        db.session.commit()
        return redirect(url_for("chat", user_id=sender_id)) #发完消息回聊天界面，user_id不变
    
    @app.route("/clear")
    def clear_messages():
        Messages.query.delete()
        db.session.commit()
        return redirect(url_for("chat"))
    
    # from app.models import User

    # @app.route("/init")
    # def init():
    #     user1 = User(name="user1", email="u1@test.com", password="123") #create acc,email/ps在models.py里comment掉了,暂放
    #     user2 = User(name="user2", email="u2@test.com", password="123")

    #     db.session.add(user1)
    #     db.session.add(user2)
    #     db.session.commit()

    #     return "Users created"