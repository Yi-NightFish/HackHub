from app import db
from datetime import datetime

# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(80), unique=True, nullable=False)
#     email = db.Column(db.String(120), unique=True, nullable=False)
#     password = db.Column(db.String(120), nullable=False)
#     is_verified = db.Column(db.Boolean, default=False)
#     university = db.Column(db.String(120), nullable=True)
#     skills = db.Column(db.String(200), nullable=True)
#     github_link = db.Column(db.String(200), nullable=True)
#     messages_sent = db.relationship('Messages', foreign_keys='Messages.sender_id', backref='sender', lazy=True)
#     messages_received = db.relationship('Messages', foreign_keys='Messages.receiver_id', backref='receiver', lazy=True)
#     organized_events = db.relationship('Event', backref='organizer', lazy=True)

#     def __repr__(self):
#         return f'<User {self.name}>'
    
# class Event(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String(120), nullable=False)
#     date = db.Column(db.DateTime, default=datetime.utcnow)
#     description = db.Column(db.Text, nullable=False)
#     organizer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
#     status = db.Column(db.String(20), nullable=False)
#     teams = db.relationship('Team', backref='event', lazy=True)
#     announcements = db.relationship('Announcement', backref='event', lazy=True)

#     def __repr__(self):
#         return f'<Event {self.title}>'
    
# class Team(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(120), nullable=False)
#     event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
#     team_code = db.Column(db.String(20), unique=True, nullable=False)
#     max_members = db.Column(db.Integer, nullable=False)
#     tasks = db.relationship('Task', backref='team', lazy=True)
#     members = db.relationship('TeamMember', backref='team', lazy=True)

#     def __repr__(self):
#         return f'<Team {self.name}>'
    
# class TeamMember(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

#     def __repr__(self):
#         return f'<TeamMember {self.team_id} - {self.user_id}>'
    
# class Task(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String(120), nullable=False)
#     team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
#     assigned_to = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
#     priority = db.Column(db.String(20), nullable=True)
#     description = db.Column(db.Text, nullable=False)
#     deadline = db.Column(db.String(20), nullable=False)
#     status = db.Column(db.String(20), nullable=False)

#     def __repr__(self):
#         return f'<Task {self.team_id} - {self.description}>'
    
# class Announcement(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
#     title = db.Column(db.String(120), nullable=False)
#     content = db.Column(db.Text, nullable=False)
#     date_posted = db.Column(db.DateTime, default=datetime.utcnow)
#     created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

#     def __repr__(self):
#         return f'<Announcement {self.title}>'
    
class Messages(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<Messages {self.sender_id} - {self.receiver_id}>'

# class Dashboard(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
#     event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
#     tasks = db.relationship('Task', backref='dashboard', lazy=True)

#     def __repr__(self):
#         return f'<Dashboard {self.user_id} - {self.event_id}>'