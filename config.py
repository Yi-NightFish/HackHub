import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "hehehehe"
    instance_path = os.path.join(basedir, 'instance')

    os.makedirs(instance_path, exist_ok = True)
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or "sqlite:///" + os.path.join(instance_path, "hackhub.db")
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = "x7186460@gmail.com"
    MAIL_PASSWORD = "chon petb yizr wcrt"
    