from flask_wtf import Form
from wtforms import StringField, PasswordField, TextAreaField, BooleanField, DecimalField, SelectField, IntegerField, RadioField
from wtforms.validators import (DataRequired, Regexp, ValidationError, Email,
                                Length, EqualTo)

from models import User, Product


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


class CreateProduct(Form):
    product_category = RadioField(
        'Category',
        validators=[DataRequired()],
        choices=[('tshirt', 'T-Shirt'), ('hat', 'Hat'), ('cd', 'CD')]
    )

    product_name = StringField(
        'Name',
        validators=[
            DataRequired(),
        ]
    )

    product_price = DecimalField(
        'Price',
        validators=[DataRequired()]
    )

    product_description = TextAreaField(
        'Description',
        validators=[DataRequired()]
    )

    one_size_stock = IntegerField('Stock')

    small_stock = IntegerField('Small Stock')

    medium_stock = IntegerField('Medium Stock')

    large_stock= IntegerField('Large Stock')


class AddAddress(Form):
    address_line_1 = StringField(
        'Address Line 1',
        validators=[DataRequired()]
    )

    address_line_2 = StringField(
        'Address Line 2',
    )

    town = StringField(
        'Town',
        validators=[DataRequired()]
    )

    city = StringField(
        'City',
        validators=[DataRequired()]
    )

    postcode = StringField(
        'Postcode',
        validators=[DataRequired()]
    )