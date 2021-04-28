from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, TextAreaField, IntegerField, PasswordField, SubmitField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Regexp
from WebApp.models import User


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')  # Form submit expressed in the html button

    def validate_username(self, username):  # Validators for existence check
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exist!')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('An account exist under this email address')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:  # Helps to submit the form without updating
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Username already exist!')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('An account exist under this email address')


class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account associated to this email')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')


# class StartTestForm(FlaskForm):
#     title = StringField('Title', validators=[DataRequired(), Length(min=2, max=20), Regexp(r'^[\w.@+-]+$')])
#     description = TextAreaField('Description', validators=[Length(max=200)])
#     iteration = IntegerField('Iterations', validators=[DataRequired()])
#     ch1 = BooleanField('Channel 1', default=False)
#     ch2 = BooleanField('Channel 2', default=False)
#     ch3 = BooleanField('Channel 3', default=False)
#     ch4 = BooleanField('Channel 4', default=False)
#     start = SubmitField('Start')
#     stop = SubmitField('Stop')
#     connect = SubmitField('Connect')


class ReviewTestForm(FlaskForm):
    tests = SelectField('Select')
    title = StringField('Title', validators=[DataRequired(), Length(min=2, max=20), Regexp(r'^[\w.@+-]+$')])
    description = TextAreaField('Description', validators=[Length(max=200)])
    submit = SubmitField('Save Changes')
    delete = SubmitField('Delete')
