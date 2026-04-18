from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from config import Config

db = SQLAlchemy()
mail = Mail()

app = Flask(__name__)
app.config.from_object(Config)
# Bind extensions to the app
db.init_app(app)
mail.init_app(app)

from app import routes, models