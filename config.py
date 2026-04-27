import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "hehehehe"
    from app import app
    os.makedirs(app.instance_path, exist_ok = True)
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or "sqlite:///" + os.path.join(app.instance_path, "hackhub.db")
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = "x7186460@gmail.com"
    MAIL_PASSWORD = "chon petb yizr wcrt"
    from functools import reduce
    app.jinja_env.globals["reduce"] = reduce
    app.jinja_env.globals["count_participants"] = lambda total, team : total + len(team.members)
    