from flask import render_template, request, redirect, url_for
from app import app, db, Messages, User

def chat_routes(app):
    @app.route("/")
    def chat():
        if "messages" not in session:
            session["messages"] = []
        return render_template("chat.html", message=session["messages"])
    
    @app.route("/send_message", methods=["POST"])
    def send_message():
        message = request.form["message"]
        session["messages"].append(message)
        return redirect(url_for("chat"))
    
    @app.route("/clear")
    def clear_messages():
        session["messages"] = []
        return redirect(url_for("chat"))