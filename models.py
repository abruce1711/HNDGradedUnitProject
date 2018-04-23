import datetime
from peewee import *
from flask_login import UserMixin
from flask_bcrypt import generate_password_hash


db = SqliteDatabase('nativesins.db')


class BaseModel(Model):
    class Meta:
        database = db


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
    one_size_stock = IntegerField(default=0)
    small_stock = IntegerField(default=0)
    medium_stock = IntegerField(default=0)
    large_stock = IntegerField(default=0)
    # create attribute to contain uploaded image location

    @classmethod
    def create_product(cls, product_category, product_name, product_price, product_description, one_size_stock,
                            small_stock, medium_stock, large_stock):
        try:
            cls.create(
                product_category=product_category,
                product_name=product_name,
                product_price=product_price,
                product_description=product_description,
                one_size_stock=one_size_stock,
                small_stock=small_stock,
                medium_stock=medium_stock,
                large_stock=large_stock
            )
        except IntegrityError:
            raise ValueError("T-Shirt with this name exists")

    @classmethod
    def update_tshirt_stock(cls, product_id, quantity, size):
        product = Product.get(Product.id == product_id)
        if size == "small":
            product.small_stock -= quantity
        elif size == "medium":
            product.medium_stock -= quantity
        elif size == "large":
            product.large_stock -= quantity
        product.save()

    @classmethod
    def update_other_stock(cls, product_id, quantity):
        product = Product.get(Product.id == product_id)
        product.one_size_stock -= quantity
        product.save()


class Order(BaseModel):
    id = PrimaryKeyField()
    user = ForeignKeyField(User, related_name='orders')
    order_date = DateField(default=datetime.datetime.now)
    order_complete = BooleanField(default=False)
    order_total = DecimalField(default=0)

    @classmethod
    def update_order_total(cls, product_id):
        total = 0
        for line in OrderLine:
            product = Product.get(Product.id == line.product_id)
            temp = product.product_price*line.quantity
            total += temp
        order = Order.get(Order.id == product_id)
        order.order_total = total
        order.save()

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
    id = PrimaryKeyField()
    product = ForeignKeyField(Product, related_name='order_line')
    order = ForeignKeyField(Order, related_name='order_lines')
    quantity = IntegerField(default=0)
    size = CharField()

    class Meta:
        database = db

    @classmethod
    def create_order_line(cls, product, order, quantity, size):
        cls.create(
            product=product,
            order=order,
            quantity=quantity,
            size=size
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
    db.create_tables([User, Product, Order, OrderLine], safe=True)
    db.close()

