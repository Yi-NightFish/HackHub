from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired
from wtforms.fields import DateTimeLocalField

class ProfileForm(FlaskForm):
    username = StringField("username", validators = [DataRequired()])
    email = StringField("email", validators = [DataRequired()])
    university = StringField("university")
    skills = StringField("skills")
    github_link = StringField("github_link")
    submit = SubmitField("Update")
    
class TaskForm(FlaskForm):
    title = StringField("Task Title", validators = [DataRequired()])
    assigned_to = SelectField("Assign Member", coerce=int)
    priority = SelectField("Priority", choices=[("High", "High"), ("Medium", "Medium"), ("Low", "Low")], validators=[DataRequired()])
    deadline = DateTimeLocalField("Deadline", format="%Y-%m-%dT%H:%M", validators=[DataRequired()])
    submit = SubmitField("Create Task")