from app import db
import datetime
import sqlalchemy as sa

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    university = db.Column(db.String(120), nullable=True, default = lambda : "")
    skills = db.Column(db.String(200), nullable=True, default = lambda : "")
    github_link = db.Column(db.String(200), nullable=True, default = lambda : "")
    messages_sent = db.relationship('Message', foreign_keys='Message.sender_id', backref='sender', lazy=True)
    messages_received = db.relationship('Message', foreign_keys='Message.receiver_id', backref='receiver', lazy=True)
    organized_events = db.relationship('Event', backref='organizer', lazy=True)
    assigned_tasks = db.relationship('Task', foreign_keys='Task.assigned_to', backref='assigned_user', lazy=True)
    team_memberships = db.relationship('Participation', backref='user', lazy=True)
    announcements = db.relationship('Announcement', backref='creator', lazy=True)

    def __repr__(self):
        return f'<User {self.name}>'
    
class OTP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120))
    code = db.Column(db.String(6))
    purpose = db.Column(db.String(20))  
    expiry = db.Column(db.DateTime)

    def __repr__(self):
        return f'<OTP {self.email}>'

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    organizer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable = False)
    end_time = db.Column(db.DateTime, nullable = False)
    cancelled = db.Column(db.Boolean, nullable = False, default = False)
    teams = db.relationship('Team', backref='event', lazy=True)
    announcements = db.relationship('Announcement', backref='event', lazy=True)

    def __repr__(self):
        return f'<Event {self.title}>'
    
    @property
    def status(self):
        if self.cancelled:
            return "cancelled"
        now = datetime.datetime.now()
        if now < self.start_time:
            return "open"
        if now > self.end_time:
            return "closed"
        return "ongoing"
    
class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    team_code = db.Column(db.String(20), unique=True, nullable=False)
    max_members = db.Column(db.Integer, nullable=False)
    tasks = db.relationship('Task', backref='team', lazy=True)
    members = db.relationship('Participation', backref='team', lazy=True)

    def __repr__(self):
        return f'<Team {self.name}>'
    
class Participation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    # Nullable team_id allows for solo participants
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=True)
    joined_at = db.Column(db.DateTime, default=datetime.datetime.now)

    event = db.relationship("Event", backref='participants', lazy=True)

    __table_args__ = (db.UniqueConstraint('user_id', 'event_id'),)

    def __repr__(self):
        return f'<Participation User:{self.user_id} Event:{self.event_id} Team:{self.team_id}>'
    
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    assigned_to = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    priority = db.Column(db.String(20), nullable=True)
    description = db.Column(db.Text, nullable=False)
    deadline = db.Column(db.DateTime, default=lambda: datetime.datetime.now(datetime.UTC), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    is_done = db.Column(db.Boolean, default=False)
    dashboard_id = db.Column(db.Integer, db.ForeignKey('dashboard.id'))

    def __repr__(self):
        return f'<Task {self.team_id} - {self.description}>'
    
class Announcement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, default=lambda: datetime.datetime.now(datetime.UTC))
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<Announcement {self.title}>'
    
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.datetime.now(datetime.UTC))
    is_read = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<Message {self.sender_id} - {self.receiver_id}>'

class Dashboard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    tasks = db.relationship('Task', backref='dashboard', lazy=True)

    def __repr__(self):
        return f'<Dashboard {self.user_id} - {self.event_id}>'
