from flask import Blueprint, request, render_template
login_bp = Blueprint("login", __name__)
@login_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        print("LOGIN:", email, password)
        return "Login successful", email
    return render_template("login.html")