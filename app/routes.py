from app import app, db
from flask import render_template
from app.forms import ProfileForm
from app.models import User

@app.route("/")
@app.route("/index")
def home():
    return render_template("home.html")

@app.route("/profile/<user_id>", methods = ["GET", "POST"])
def profile(user_id):
    profile_page = ProfileForm()
    user = db.session.get(User, user_id)

    # Mock that user has signed in. Remove current_user argument when using flask_login extension because current_user argument is automatically set
    return render_template("profile.html", form = profile_page, user = user, current_user = user)
