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


class AddressDetails(BaseModel):
    user_id = ForeignKeyField(User, related_name='address')
    address_line_1 = CharField()
    address_line_2 = CharField()
    town = CharField()
    city = CharField()
    postcode = CharField()

    @classmethod
    def add_address(cls, user_id, address_line_1, address_line_2, town, city, postcode):
        cls.create(
            user_id=user_id,
            address_line_1=address_line_1,
            address_line_2=address_line_2,
            town=town,
            city=city,
            postcode=postcode
        )


class Product(BaseModel):
    id = PrimaryKeyField()
    product_category = CharField()
    product_name = CharField()
    product_price = DecimalField(default=0)
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
    def reduce_tshirt_stock(cls, product_id, quantity, size):
        product = Product.get(Product.id == product_id)
        if size == "small":
            product.small_stock -= quantity
        elif size == "medium":
            product.medium_stock -= quantity
        elif size == "large":
            product.large_stock -= quantity
        product.save()

    @classmethod
    def reduce_other_stock(cls, product_id, quantity):
        product = Product.get(Product.id == product_id)
        product.one_size_stock -= quantity
        product.save()

    @classmethod
    def increase_tshirt_stock(cls, product_id, quantity, size):
        product = Product.get(Product.id == product_id)
        if size == "small":
            product.small_stock += quantity
        elif size == "medium":
            product.medium_stock += quantity
        elif size == "large":
            product.large_stock += quantity
        product.save()

    @classmethod
    def increase_other_stock(cls, product_id, quantity):
        product = Product.get(Product.id == product_id)
        product.one_size_stock += quantity
        product.save()

    @classmethod
    def tshirt__in_stock(cls, quantity, product_id, size):
        product = Product.get(Product.id == product_id)
        if size == "small":
            if quantity > product.small_stock:
                return False
            else:
                return True
        elif size == "medium":
                if quantity > product.medium_stock:
                    return False
                else:
                    return True
        elif size == "large":
                if quantity > product.large_stock:
                    return False
                else:
                    return True

    @classmethod
    def other_in_stock(cls, quantity, product_id):
        product = Product.get(Product.id == product_id)
        if quantity > product.one_size_stock:
            return False
        else:
            return True


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
    db.create_tables([User, AddressDetails, Product, Order, OrderLine], safe=True)
    db.close()

