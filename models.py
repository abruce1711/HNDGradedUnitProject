import datetime
from peewee import *
from flask_login import UserMixin
from flask_bcrypt import generate_password_hash


db = SqliteDatabase('nativesins.db')


class User(UserMixin, Model):
    first_name = CharField()
    last_name = CharField()
    email_address = CharField(unique=True)
    password = CharField(max_length=100)
    user_role = CharField(default='customer')

    class Meta:
        database = db

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


def initialize():
    db.connect()
    db.create_tables([User], safe=True)
    db.close()

