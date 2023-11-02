from typing import Union
from wtforms import StringField, SubmitField, TextAreaField, PasswordField
from wtforms.validators import DataRequired, Length, ValidationError
from flask_wtf.file import FileField, FileAllowed
from Engine.helpers import CheckProfanity
from flask_wtf import FlaskForm
from Engine.models import User

class ProfileForm(FlaskForm):

    submit: SubmitField = SubmitField('Update')
    
    banner: TextAreaField = TextAreaField(id="motto", validators=[DataRequired(),Length(min=20, max=200), CheckProfanity()])
    
    profilePicture: FileField = FileField(id='profile-picture-input', validators=[FileAllowed(['jpeg', 'png', 'jpg', 'webp'])])
    
    username: StringField = StringField(id='username', validators=[DataRequired(), Length(max=50), CheckProfanity()])
    
    def validate_username(self, username) -> Union[None, ValidationError]:
        if User.query.filter_by(username=username.data) == True:
            raise ValidationError("Username already taken")

class DeleteAccountForm(FlaskForm):
    
    submit: SubmitField = SubmitField('Delete', id="delete-account-proceed")
    
    password: PasswordField = PasswordField(id='delete-account-password-input', validators=[DataRequired()])
    