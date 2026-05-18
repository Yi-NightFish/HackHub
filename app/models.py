from app import db
import datetime
import datetime as dt
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
    last_seen = db.Column(db.DateTime, default=lambda: datetime.datetime.now(datetime.UTC))

    def is_online(self):
        if self.last_seen is None:
            return False
        now = datetime.datetime.now(datetime.UTC).replace(tzinfo=None)
        # Consider user online if last seen within the last 5 minutes
        return (now - self.last_seen) < datetime.timedelta(minutes=1)

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
    deadline = db.Column(db.DateTime, nullable = False)
    cancelled = db.Column(db.Boolean, nullable = True, default = False)
    teams = db.relationship('Team', backref='event', lazy=True)
    announcements = db.relationship('Announcement', backref='event', lazy=True)

    def __repr__(self):
        return f'<Event {self.title}>'
    
    @property
    def status(self):
        if self.cancelled:
            return "cancelled"
        now = datetime.datetime.now()
        if now < self.deadline:
            return "open"
        if now > self.end_time:
            return "completed"
        return "ongoing"
    
class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    motto = db.Column(db.String(200), nullable=True)
    roles = db.Column(db.String(300), nullable=True)
    project_idea = db.Column(db.Text, nullable=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    leader_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    team_code = db.Column(db.String(20), unique=True, nullable=False)
    max_members = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.datetime.now())
    project_submitted = db.Column(db.Boolean, default=False)
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
    roles = db.Column(db.String(300), nullable=True)
    __table_args__ = (db.UniqueConstraint('team_id', 'user_id', name = "uq_team_user"),)

    def __repr__(self):
        return f'<Participation User:{self.user_id} Event:{self.event_id} Team:{self.team_id}>'

class TeamJoinRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), default="Pending")
    created_at = db.Column(db.DateTime, default=lambda: datetime.datetime.now())
    team = db.relationship('Team', backref='join_requests')
    user = db.relationship('User', backref='team_join_requests')
    
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    assigned_to = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    priority = db.Column(db.String(20), nullable=True)
    description = db.Column(db.Text, nullable=True)
    deadline = db.Column(db.DateTime, default=lambda: datetime.datetime.now(datetime.UTC), nullable=False)
    status = db.Column(db.String(30), nullable=False, default="To Do")
    is_done = db.Column(db.Boolean, default=False)
    dashboard_id = db.Column(db.Integer, db.ForeignKey('dashboard.id'))
    subtasks = db.relationship('Subtask', backref='task', lazy=True, cascade="all, delete")
    def __repr__(self):
        return f'<Task {self.team_id} - {self.description}>'
    
class Subtask(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
   title = db.Column(db.String(120), nullable=False)
   description = db.Column(db.Text, nullable=True)
   assigned_to = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
   priority = db.Column(db.String(20), nullable=True)
   deadline = db.Column(db.DateTime, nullable=True)
   status = db.Column(db.String(30), nullable=False, default="Wishlist")
   is_done = db.Column(db.Boolean, default=False)
   assigned_user = db.relationship('User', foreign_keys=[assigned_to])

   def __repr__(self):
       return f'<Subtask {self.task_id} - {self.title}>'
    
class TaskActivity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    action = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.datetime.now())
    task = db.relationship('Task', backref='activities')
    user = db.relationship('User', backref='task_activities')

    def __repr__(self):
        return f'<TaskActivity {self.action}>'
    
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
    timestamp = db.Column(db.DateTime, default=lambda: datetime.datetime.now())
    is_read = db.Column(db.Boolean, default=False)
    # deleted_by_sender = db.Column(db.Boolean, default=False)
    # deleted_by_receiver = db.Column(db.Boolean, default=False)
    is_deleted = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<Message {self.sender_id} - {self.receiver_id}>'
    
class ChatVisibility(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    other_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    visible_since = db.Column(db.DateTime, default=lambda: datetime.datetime.now(1970, 1, 1))

    def __repr__(self):
        return f'<ChatVisibility {self.user_id} - {self.other_user_id}>'

class Dashboard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    tasks = db.relationship('Task', backref='dashboard', lazy=True)

    def __repr__(self):
        return f'<Dashboard {self.user_id} - {self.event_id}>'

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False, unique=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    tech_stack = db.Column(db.String(300), nullable=True)
    demo_link = db.Column(db.String(300), nullable=True)
    github_link = db.Column(db.String(300), nullable=True)
    screenshots_link = db.Column(db.Text, nullable=True)
    contributions = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.datetime.now(datetime.UTC))
    team = db.relationship('Team', backref='project')
    
    def __repr__(self):
        return f'<Project {self.title}>'