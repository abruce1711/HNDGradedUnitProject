import datetime
from peewee import *
from flask_login import UserMixin
from flask_bcrypt import generate_password_hash


db = SqliteDatabase('nativesins.db')


class BaseModel(Model):
    class Meta:
        database=db


class User(UserMixin, BaseModel):
    id = PrimaryKeyField()
    first_name = CharField()
    last_name = CharField()
    email_address = CharField(unique=True)
    password = CharField(max_length=100)
    user_role = CharField(default='customer')

    @classmethod
    def create_user(cls, first_name, last_name, email_address, password, user_role):
        try:
            cls.create(
                first_name=first_name,
                last_name=last_name,
                email_address=email_address,
                password=generate_password_hash(password),
                user_role=user_role
            )
        except IntegrityError:
            raise ValueError("User already exists")


class Product(BaseModel):
    id = PrimaryKeyField()
    product_name = CharField()
    product_category = CharField()
    product_price = DecimalField()
    product_description = CharField()
    product_stock_level = IntegerField()
    # create attribute to contain uploaded image location

    @classmethod
    def create_product(cls, name, category, size, price, description, stock):
        try:
            cls.create(
                product_name=name,
                product_category=category,
                product_size=size,
                product_price=price,
                product_description=description,
                product_stock_level=stock
            )
        except IntegrityError as e:
            raise ValueError(e)


def initialize():
    db.connect()
    db.create_tables([User, Product], safe=True)
    db.close()

