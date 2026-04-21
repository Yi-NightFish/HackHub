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