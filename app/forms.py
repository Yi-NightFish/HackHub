from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, TextAreaField, DateTimeLocalField
from wtforms.validators import DataRequired, Optional

class ProfileForm(FlaskForm):
    username = StringField("username", validators = [DataRequired()])
    email = StringField("email", validators = [DataRequired()])
    university = StringField("university")
    skills = StringField("skills")
    github_link = StringField("github_link")
    submit = SubmitField("Update")
    
class TaskForm(FlaskForm):
    title = StringField("Task Title", validators = [DataRequired()])
    description = TextAreaField("Task Description", validators = [Optional()])
    status = SelectField("Status", choices=[("Wishlist", "Wishlist"), ("To Do", "To Do"), ("In Progress", "In Progress"), ("In Review", "In Review"), ("Complete", "Complete")])
    assigned_to = SelectField("Assign Member", coerce=int)
    priority = SelectField("Priority", choices=[("High", "High"), ("Medium", "Medium"), ("Low", "Low")], validators=[DataRequired()])
    deadline = DateTimeLocalField("Deadline", format="%Y-%m-%dT%H:%M", validators=[DataRequired()])
    submit = SubmitField("Create Task")