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

    @classmethod
    def update_stock(cls, product_id, size, quantity, add_or_reduce):
        if add_or_reduce == "reduce":
            if size == "small":
                new_stock = cls.small_stock_level - quantity
                product = cls(id=product_id, small_stock_level=new_stock)
                product.save()
            elif size == "medium":
                new_stock = cls.medium_stock_level - quantity
                product = cls(id=product_id, medium_stock_level=new_stock)
                product.save()
            elif size == "large":
                new_stock = cls.large_stock_level - quantity
                product = cls(id=product_id, large_stock_level=new_stock)
                product.save()
        else:
            if size == "small":
                new_stock = cls.small_stock_level + quantity
                product = cls(id=product_id, small_stock_level=new_stock)
                product.save()
            elif size == "medium":
                new_stock = cls.medium_stock_level + quantity
                product = cls(id=product_id, medium_stock_level=new_stock)
                product.save()
            elif size == "large":
                new_stock = cls.large_stock_level + quantity
                product = cls(id=product_id, large_stock_level=new_stock)
                product.save()


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

    @classmethod
    def update_stock(cls, product_id, quantity, add_or_reduce):
        if add_or_reduce == "reduce":
            new_stock = cls.stock_level - quantity
        else:
            new_stock = cls.stock_level + quantity
        product = cls(id=product_id, stock_level=new_stock)
        product.save()


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

    @classmethod
    def update_stock(cls, product_id, quantity, add_or_reduce):
        if add_or_reduce == "reduce":
            new_stock = cls.stock_level - quantity
        else:
            new_stock = cls.stock_level + quantity
        product = cls(id=product_id, stock_level=new_stock)
        product.save()


class Order(Model):
    user = ForeignKeyField(User, related_name='orders')
    order_date = DateField(default=datetime.datetime.now)
    order_complete = BooleanField(default=False)
    order_total = DecimalField(default=0)

    class Meta:
        database = db

    @classmethod
    def create_order(cls, user):
        cls.create(user=user)

    @classmethod
    def find_current_order(cls, user):
        if user.is_authenticated:
            orders = user.orders.select()
            for order in orders:
                if not order.order_complete:
                    return order
                else:
                    return None
        else:
            return None

    @classmethod
    def get_current_basket(cls, order, user):
        if user.is_authenticated and order != None:
            current_basket = 0
            for line in order.order_lines:
                current_basket += line.quantity
            return current_basket
        else:
            return None


class OrderLine(Model):
    product = ForeignKeyField(Product, related_name='order_line')
    order = ForeignKeyField(Order, related_name='order_lines')
    quantity = IntegerField(default=0)

    class Meta:
        database = db

    @classmethod
    def create_order_line(cls, product, order, quantity):
        cls.create(
            product=product,
            order=order,
            quantity=quantity
        )

    @classmethod
    def remove_order_line(cls, order_line_id):
        order_line = cls.get(id=order_line_id)
        order_line.delete_instance()

    @classmethod
    def update_line_quantity(cls, order_line_id, quantity_to_add):
        new_quantity = cls.quantity + quantity_to_add
        order_line = cls(id=order_line_id, quantity=new_quantity)
        order_line.save()


def initialize():
    db.connect()
    db.create_tables([User, Tshirt, Hat, CD, Order, OrderLine], safe=True)
    db.close()

