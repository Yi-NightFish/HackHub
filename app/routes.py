from flask import render_template, request, redirect, url_for
from app import db
from app.models import Messages
# from datetime import datetime

def chat_routes(app):
    @app.route("/")
    def chat():
        messages = Messages.query.order_by(Messages.timestamp.asc()).all()  #取数据from旧到新
        return render_template("chat.html", messages=messages)
    
    @app.route("/send_message", methods=["POST"])
    def send_message():
        message = request.form["message"]
        new_message = Messages(message=message, sender_id=1, receiver_id=2) #1/2是临时用户
        db.session.add(new_message)
        db.session.commit()
        return redirect(url_for("chat"))
    
    @app.route("/clear")
    def clear_messages():
        Messages.query.delete()
        db.session.commit()
        return redirect(url_for("chat"))
    
    from app.models import User

    @app.route("/init")
    def init():
        user1 = User(name="user1", email="u1@test.com", password="123")
        user2 = User(name="user2", email="u2@test.com", password="123")

        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()

        return "Users created"