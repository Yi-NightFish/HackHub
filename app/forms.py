from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired

class ProfileForm(FlaskForm):
    username = StringField("username", validators = [DataRequired()])
    email = StringField("email", validators = [DataRequired()])
    university = StringField("university",  validators = [DataRequired()])
    skills = StringField("skills", validators = [DataRequired()])
    github_link = StringField("github_link", validators = [DataRequired()])
    submit = SubmitField("Update")
