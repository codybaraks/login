from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Email, Length, Regexp


class RegisterForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=4, message="Your name is too short")])
    surname = StringField('Name', validators=[DataRequired(), Length(min=4, message="Your name is too short")])
    email = StringField('Email', validators=[DataRequired(), Email(message="Invalid Email")])
    password = PasswordField('Password', validators=[DataRequired(message="You must provide a password"),
                                                     Length(min=6, message="Password Too short")])


class ResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(message="Invalid Email")])


class UserLoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(),Email(message="Invalid Emaill")])
    password = PasswordField('Password', validators=[DataRequired(message="You must provide a password"), Length(min=3,  message="Password Too short")])


