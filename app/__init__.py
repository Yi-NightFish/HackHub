from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
from config import Config

db = SQLAlchemy(app)
migrate = Migrate(app, db)
mail = Mail(app)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    with app.app_context():
        from app import routes, models
        from app.routes import chat_routes
        chat_routes(app)

    return app