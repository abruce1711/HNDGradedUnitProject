from flask_wtf import Form
from wtforms import StringField, PasswordField, TextAreaField, BooleanField, DecimalField, SelectField, IntegerField
from wtforms.validators import (DataRequired, Regexp, ValidationError, Email,
                                Length, EqualTo)

from models import User


# custom validator
def email_exists(form, field):
    if User.select().where(User.email_address == field.data).exists():
        raise ValidationError('User with that email already exists')


class LoginForm(Form):
    email_address = StringField(
        'Email',
        validators=[DataRequired(), Email()]
    )

    password = PasswordField(
        'Password',
        validators=[DataRequired()]
    )


class RegisterForm(Form):
    first_name = StringField(
        'First Name',
        validators=[DataRequired()]
    )

    last_name = StringField(
        'Last Name',
        validators=[DataRequired()]
    )

    email = StringField(
        'Email',
        validators=[
            DataRequired(),
            Email(),
            email_exists
        ]
    )

    password = PasswordField(
        'Password',
        validators=[
            DataRequired(),
            Length(min=8),
            EqualTo('password2', message="Passwords must match"),
        ]
    )

    password2 = PasswordField(
        'Re-enter Password',
        validators=[DataRequired()]
    )


class CreateUser(RegisterForm, Form):
    user_role = SelectField(
        choices=[
            ('blank', 'Please select user role'), ('customer', 'Customer'), ('staff', 'Staff'), ('admin', 'Admin')
        ]
    )
