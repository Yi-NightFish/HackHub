from app import app
from flask import render_template
from app.forms import ProfileForm

@app.route("/")
@app.route("/index")
def home():
    return render_template("home.html")

@app.route("/profile")
def profile():
    profile_page = ProfileForm()
    return render_template("profile.html", form = profile_page)
