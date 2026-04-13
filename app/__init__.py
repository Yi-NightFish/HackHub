from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
from config import Config
app.config.from_object(Config)
db = SQLAlchemy(app)

from app import routes, models
