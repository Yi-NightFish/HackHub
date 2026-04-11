from flask import Blueprint, render_template, request, redirect
register_bp = Blueprint("register", __name__)
@register_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        print("REGISTER:", email, password)
        return redirect("/login")
    return render_template("register.html")