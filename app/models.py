from app import db, app

# Reflect the existing SQLite schema into SQLAlchemy metadata before binding ORM classes.
# This ensures `db.metadata.tables[...]` is populated from hackhub.sqlite.
app.app_context().push()  # Push application context to access current_app and db
db.metadata.reflect(bind=db.engine)

class User(db.Model):
    __table__ = db.metadata.tables['user']

class Event(db.Model):
    __table__ = db.metadata.tables['event']

class Team(db.Model):
    __table__ = db.metadata.tables['team']

class TeamMember(db.Model):
    __table__ = db.metadata.tables['team_member']

class Task(db.Model):
    __table__ = db.metadata.tables['task']

class Announcement(db.Model):
    __table__ = db.metadata.tables['announcement']

class Messages(db.Model):
    __table__ = db.metadata.tables['messages']
