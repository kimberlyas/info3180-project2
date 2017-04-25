from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import PasswordField, StringField, TextAreaField, SelectField
from wtforms.validators import InputRequired, Email, Regexp, Length, URL
from models import UserProfile

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired(), 
                                                     Regexp('/^(?=.*[A-Za-z])(?=.*\d)(?=.*[$@$!%*#?&])[A-Za-z\d$@$!%*#?&]{8,}$/', message="Password regex invalid"),
                                                     Length(min=8, message="Password must be at least 8 characters")])

# Extends LoginForm to include more fields and overwrite some methods
class SignupForm(LoginForm):
    name = StringField('Full Name', validators=[InputRequired()])
    age = StringField('Age', validators=[InputRequired()])
    image = FileField('User Pic', validators=[FileAllowed(['png', 'jpg', 'jpeg', 'gif'], 'Images only!')])
    gender = SelectField('Gender', choices = [('F', 'Female'), 
      ('M', 'Male'), ('O', 'Other')])
    
    def __init__(self, *args, **kwargs):
      FlaskForm.__init__(self, *args, **kwargs)
 
    def validate(self):
      """ Ensures a unique email address is given """
      if not FlaskForm.validate(self):
        return False
     
      # Check if email is already in the database
      user = UserProfile.query.filter_by(email=self.email.data).first()
      if user:
        # Error message
        self.email.errors.append('This email address is already being used.')
        return False
      else:
        return True

# class WishlistForm(FlaskForm):
#     title = StringField('Title', validators=[InputRequired()])
#     description = TextAreaField('Description', validators=[InputRequired()])
#     url = StringField('Item URL', validators=[InputRequired(), URL(message="Invalid URL given")])
    