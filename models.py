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
    product_category = CharField()
    product_name = CharField()
    product_price = DoubleField()
    product_description = CharField()
    # create attribute to contain uploaded image location


class Tshirt(Product):
    small_stock_level = IntegerField(default=0)
    medium_stock_level = IntegerField(default=0)
    large_stock_level = IntegerField(default=0)

    @classmethod
    def create_tshirt(cls, product_category, product_name, product_price, product_description,
                      small_stock_level, medium_stock_level, large_stock_level):
        try:
            cls.create(
                product_category=product_category,
                product_name=product_name,
                product_price=product_price,
                product_description=product_description,
                small_stock_level=small_stock_level,
                medium_stock_level=medium_stock_level,
                large_stock_level=large_stock_level
            )
        except IntegrityError:
            raise ValueError("T-Shirt with this name exists")


class Hat(Product):
    stock_level = IntegerField(default=0)

    @classmethod
    def create_hat(cls, product_category, product_name, product_price, product_description, stock_level):
        try:
            cls.create(
                product_category=product_category,
                product_name=product_name,
                product_price=product_price,
                product_description=product_description,
                stock_level=stock_level,
            )
        except IntegrityError:
            raise ValueError("Hat with this name exists")


class CD(Product):
    stock_level = IntegerField(default=0)

    @classmethod
    def create_cd(cls, product_category, product_name, product_price, product_description, stock_level):
        try:
            cls.create(
                product_category=product_category,
                product_name=product_name,
                product_price=product_price,
                product_description=product_description,
                stock_level=stock_level,
            )
        except IntegrityError:
            raise ValueError("CD with this name exists")


def initialize():
    db.connect()
    db.create_tables([User, Tshirt, Hat, CD], safe=True)
    db.close()

