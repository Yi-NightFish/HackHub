from flask import render_template, request, redirect, url_for, session
from app import db
from models import Messages, User

def chat_routes(app):
    @app.route("/")
    def chat():
        messages = Messages.query.order_by(Messages.timestamp.asc()).all()  #取数据from旧到新
        return render_template("chat.html", message=messages)
    
    @app.route("/send_message", methods=["POST"])
    def send_message():
        message = request.form["message"]
        new_message = Messages(message=message)
        db.session.add(new_message)
        db.session.commit()
        return redirect(url_for("chat"))
    
    @app.route("/clear")
    def clear_messages():
        Messages.query.delete()
        db.session.commit()
        return redirect(url_for("chat"))