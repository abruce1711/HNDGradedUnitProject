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

    @classmethod
    def edit_details(cls, user_id, first_name, last_name, email_address):
        try:
            query = cls.update(
                first_name=first_name,
                last_name=last_name,
                email_address=email_address
            ).where(cls.id == user_id)
            query.execute()
        except IntegrityError:
            raise ValueError("User with that email address already exists")

    @classmethod
    def reset_password(cls, user_id, password):
        query = cls.update(
            password=generate_password_hash(password)
        ).where(cls.id == user_id)
        query.execute()


class AddressDetails(BaseModel):
    id = PrimaryKeyField()
    user_id = ForeignKeyField(User, related_name='address')
    address_line_1 = CharField()
    address_line_2 = CharField()
    town = CharField()
    city = CharField()
    postcode = CharField()
    default = BooleanField(default=False)

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
        return cls.id

    @classmethod
    def edit_address(cls, address_id, address_line_1, address_line_2, town, city, postcode):
        query = cls.update(
            address_line_1=address_line_1,
            address_line_2=address_line_2,
            town=town,
            city=city,
            postcode=postcode
        ).where(cls.id == address_id)
        query.execute()

    @classmethod
    def delete_address(cls, address_id):
        address = cls.get(cls.id == address_id)
        address.delete_instance()

    @classmethod
    def get_default_address(cls, user_id):
        default_address = None
        address_query = cls.select().where(cls.user_id == user_id)
        if address_query.exists() and address_query is not None:
            for address in address_query:
                if address.default is True:
                    default_address = address
        return default_address

    @classmethod
    def change_default(cls, new_default_id, user_id):
        old_default = cls.get_default_address(user_id)
        new_default = cls.get(cls.id == new_default_id)
        if old_default is None:
            new_default.default = True
            new_default.save()
        else:
            old_default.default = False
            new_default.default = True
            old_default.save()
            new_default.save()


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
    address = ForeignKeyField(AddressDetails, related_name='address', null=True)
    order_date = DateField(default=datetime.datetime.now)
    order_complete = BooleanField(default=False)
    order_total = DecimalField(default=0)

    @classmethod
    def update_order_total(cls, order_id):
        total = 0
        order_lines = OrderLine.select().where(OrderLine.order == order_id)
        for line in order_lines:
            product = Product.get(Product.id == line.product_id)
            temp = product.product_price*line.quantity
            total += temp
        order = Order.get(Order.id == order_id)
        order.order_total = total
        order.save()

    @classmethod
    def create_order(cls, user):
        cls.create(user=user)

    @classmethod
    def create_order_with_address(cls, user, address):
        cls.create(
            user=user,
            address=address
        )

    @classmethod
    def add_address_to_order(cls, order_id, address):
        order = cls.get(cls.id == order_id)
        order.address = address
        order.save()

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
    def increase_line_quantity(cls, order_line_id, quantity_to_add):
        new_quantity = cls.quantity + quantity_to_add
        order_line = cls(id=order_line_id, quantity=new_quantity)
        order_line.save()

    @classmethod
    def edit_line_quantity(cls, order_line_id, new_quantity):
        order_line = cls(id=order_line_id, quantity=new_quantity)
        order_line.save()


def initialize():
    db.connect()
    db.create_tables([User, AddressDetails, Product, Order, OrderLine], safe=True)
    db.close()

