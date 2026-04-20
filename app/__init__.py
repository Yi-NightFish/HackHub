from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hackhub.db'
    app.secret_key = "secret"

    db.init_app(app)

    from app.routes import chat_routes
    chat_routes(app)

    return app