# all imports for the app to work
from flask import (Flask, g, render_template, flash, redirect, url_for, abort, request, session)
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import check_password_hash

import forms
import models

# creates instance of the flask class and if the script is run directly
# it gets the name "__main__"
app = Flask(__name__)

# Flask needs a secret key to create session objects, this one is randomly generated
# and is used to cryptographically sign user cookies to prevent them being modified
app.secret_key = "dvapvhsdfbvasoifjsfobmskdfnv394t5e943i-4"

# creates an instance of the LoginManager class and passes
# in the Flask object from above
login_manager = LoginManager(app)

# the login view is where the app will redirect non_authenticated users
# if @login_required is set
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(userid):
    """Loads a user from the user id stored in the cookies."""

    try:
        return models.User.get(models.User.id == userid)
    except models.DoesNotExist:
        return None


@app.before_request
def before_request():
    """Connect to the database before each request."""

    g.db = models.db
    g.db.connect()
    g.user = current_user

    g.current_order = models.Order.find_current_order(current_user)
    g.current_basket = models.Order.get_current_basket(g.current_order, current_user)
    try:
        g.default_address = models.AddressDetails.get_default_address(current_user.id)
    except AttributeError:
        g.default_address = None


@app.after_request
def after_request(response):
    """Close database connection after each request"""

    g.db.close()
    return response


# app.route is the path after the domain in the URL
# methods is if data will be POST, GOT, or both
@app.route('/login', methods=('GET', 'POST'))
def login():
    """Compares credentials to details in the database and logs the user in if they match.

    Creates a cookie in the browser to tell the webapp that the user is authenticated."""

    # instance of LoginForm in forms.py
    form = forms.LoginForm()
    # if the form is submitted without errors
    if form.validate_on_submit():
        try:
            # query the db to find a user email address equal to the one given
            user = models.User.get(models.User.email_address == form.email_address.data)
        except models.DoesNotExist:
            # errors if not found
            flash("Email or password incorrect", "error")
        else:
            # check password hash is a method from the bcrypt library imported
            # it compares the password given to the encrypted password in the db
            # and returns true or false
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                flash("Log in successful", "success")
                return redirect(url_for('index'))
            else:
                # flash messaging appears at the top of the screen
                # the category given second is used to style the message
                flash("Email or password incorrect", "error")
    # render_template returns one of the page templates
    return render_template('login.html', form=form)


@app.route('/register', methods=('GET', 'POST'))
def register():
    """Route that returns registration page

    On this route it uses a User method to create a user in the database
    using details given by the user.
    """

    form = forms.RegisterForm()
    if form.validate_on_submit():
        # method from the User model that creates user in db
        models.User.create_user(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email_address=form.email.data,
            password=form.password.data,
            user_role="customer"
        )
        flash("Account Created", "success")
        user = models.User.get(models.User.email_address == form.email.data)
        login_user(user)
        return redirect(url_for('index'))
    return render_template('register.html', form=form)


@app.route('/logout')
@login_required
def logout():
    """Removes user cookies to log user out of web app"""

    logout_user()
    flash("Logged out", "success")
    return redirect(url_for('login'))


@app.route('/create_user', methods=('GET', 'POST'))
# redirects to login if the user isn't authenticated
@login_required
def create_user():
    """Route that returns the page for administrators to create user accounts.

    On this route it uses a User method to create a user in the database
    using details given by the administrator, unlike the registration, this one
    includes user role.
    """

    form = forms.CreateUser()
    # if the user isn't an admin
    if current_user.user_role != "admin":
        # return a 404 error
        abort(404)
    else:
        if form.validate_on_submit():
            if form.user_role.data == "blank":
                flash("Must select user role", "error")
            else:
                models.User.create_user(
                    first_name=form.first_name.data.title(),
                    last_name=form.last_name.data.title(),
                    email_address=form.email.data,
                    password=form.password.data,
                    user_role=form.user_role.data
                )
                flash("User created", "success")
                return redirect(url_for('create_user'))
        return render_template('create_user.html', form=form, current_basket=g.current_basket)


@app.route('/account/<int:user_id>')
@login_required
def account(user_id):
    if current_user.id != user_id:
        abort(404)
    else:
        return render_template('account.html', current_basket=g.current_basket)


@app.route('/addresses/<int:user_id>')
def addresses(user_id):
    address_list = models.AddressDetails.select()
    return render_template('addresses.html', current_basket=g.current_basket, address_list=address_list)


@app.route('/add_address', methods=('POST', 'GET'))
@login_required
def add_address():
    form = forms.AddAddress()
    if form.validate_on_submit():
        models.AddressDetails.add_address(
            user_id=current_user.id,
            address_line_1=form.address_line_1.data,
            address_line_2=form.address_line_2.data,
            town=form.town.data,
            city=form.city.data,
            postcode=form.postcode.data
        )
        address = models.AddressDetails.select().order_by(models.AddressDetails.id.desc()).get()
        models.AddressDetails.change_default(address.id, current_user.id)
        if g.current_order is not None:
            models.Order.add_address_to_order(g.current_order.id, address.id)
        flash("Address added", "success")
        if session.get('checking out'):
            session.pop('checking out', None)
            return redirect(url_for('checkout'))
        else:
            return redirect(url_for('add_address'))
    return render_template('add_address.html', form=form, current_basket=g.current_basket)


@app.route('/create_product', methods=('GET', 'POST'))
@login_required
def create_product():
    """Route that returns the page for administrators to create products.

    On this route it takes input from the create product form and
    uses a method inside the Product class to create a product
    in the database.
    """

    form = forms.CreateProduct()

    # if the user is a customer, give them a 404 page
    if current_user.user_role == "customer":
        abort(404)
    else:
        # if the form is validated
        if form.validate_on_submit():
            models.Product.create(
                product_category=form.product_category.data,
                product_name=form.product_name.data,
                product_price=form.product_price.data,
                product_description=form.product_description.data,
                one_size_stock=form.one_size_stock.data,
                small_stock=form.small_stock.data,
                medium_stock=form.medium_stock.data,
                large_stock=form.large_stock.data
            )
            flash("Product added", "success")
            return redirect(url_for('create_product'))
        # returns the create_product template
        return render_template('create_product.html', form=form, current_basket=g.current_basket)


@app.route('/products', methods=('POST', 'GET'))
def products():
    sorting_form = forms.OrderProducts()
    product_list = models.Product.select().order_by(models.Product.product_name)
    if sorting_form.validate_on_submit():
        sort_by = sorting_form.order_by.data
        if sort_by == "price_lth":
            product_list = models.Product.select().order_by(models.Product.product_price)
        elif sort_by == "price_htl":
            product_list = models.Product.select().order_by(models.Product.product_price.desc())
        elif sort_by == 'alphabet':
            product_list = models.Product.select().order_by(models.Product.product_name)
    return render_template('products.html', products=product_list,
                           current_basket=g.current_basket, sorting_form=sorting_form)


@app.route('/remove_product/<int:product_id>')
@login_required
def remove_product(product_id):
    if current_user.user_role == "customer":
        abort(404)
    else:
        product_list = models.Product.select()
        product = models.Product.get(models.Product.id == product_id)
        product.delete_instance()
        flash("Product deleted", "success")
        return redirect(url_for('products', products=product_list, current_basket=g.current_basket))


@app.route('/add_to_order/<int:product_id>/<product_category>', methods=('POST', 'GET'))
@login_required
def add_to_order(product_id, product_category):
    if request.method == 'POST':
        quantity = int(request.form.get('quantity'))
        size = request.form.get('size')
        if g.current_order:
            for line in g.current_order.order_lines:
                if product_category == "tshirt":
                    if product_id == line.product_id and size == line.size:
                        if models.Product.tshirt__in_stock(quantity, product_id, size):
                            models.OrderLine.update_line_quantity(line.id, quantity)
                            models.Product.reduce_tshirt_stock(product_id, quantity, size)
                            flash("Added to basket", "success")
                        else:
                            flash("Please enter a quantity less than the stock", "error")
                        break
                else:
                    if product_id == line.product_id:
                        if models.Product.other_in_stock(quantity, product_id):
                            models.OrderLine.update_line_quantity(line.id, quantity)
                            models.Product.reduce_other_stock(product_id, quantity)
                            flash("Added to basket", "success")
                        else:
                            flash("Please enter a quantity less than the stock", "error")
                        break
            else:
                if product_category == "tshirt":
                    if models.Product.tshirt__in_stock(quantity, product_id, size):
                        models.OrderLine.create_order_line(product_id, g.current_order.id, quantity, size=size)
                        models.Product.reduce_tshirt_stock(product_id, quantity, size)
                        flash("Added to basket", "success")
                    else:
                        flash("Please enter a quantity less than the stock", "error")
                else:
                    if models.Product.other_in_stock(quantity, product_id):
                        models.OrderLine.create_order_line(product_id, g.current_order.id, quantity, size="one_size")
                        models.Product.reduce_other_stock(product_id, quantity)
                        flash("Added to basket", "success")
                    else:
                        flash("Please enter a quantity less than the stock", "error")
            models.Order.update_order_total(g.current_order.id)
        else:
            if g.default_address is not None:
                models.Order.create_order_with_address(current_user.id, g.default_address.id)
            else:
                models.Order.create_order(current_user.id)
            g.current_order = models.Order.find_current_order(current_user)
            if product_category == "tshirt":
                if models.Product.tshirt__in_stock(quantity, product_id, size):
                    models.OrderLine.create_order_line(product_id, g.current_order.id, quantity, size=size)
                    models.Product.reduce_tshirt_stock(product_id, quantity, size)
                    flash("Added to basket", "success")
                else:
                    flash("Please enter a quantity less than the stock", "error")
            else:
                if models.Product.other_in_stock(quantity, product_id):
                    models.OrderLine.create_order_line(product_id, g.current_order.id, quantity, size="one_size")
                    models.Product.reduce_other_stock(product_id, quantity)
                    flash("Added to basket", "success")
                else:
                    flash("Please enter a quantity less than the stock", "error")
            models.Order.update_order_total(g.current_order.id)
    return redirect(url_for('products'))


@app.route('/basket/<int:user_id>')
@login_required
def basket(user_id):
    if current_user.id != user_id:
        abort(404)
    else:
        return render_template('basket.html', current_basket=g.current_basket, current_order=g.current_order)


@app.route('/remove_from_basket/<int:line_id>/<int:quantity>')
@login_required
def remove_from_basket(line_id, quantity):
    line = models.OrderLine.get(models.OrderLine.id == line_id)
    product = models.Product.get(models.Product.id == line.product_id)
    order = models.Order.get(models.Order.id == line.order_id)
    if order.user_id != current_user.id:
        abort(404)
    else:
        if product.product_category == "tshirt":
            models.Product.increase_tshirt_stock(product.id, quantity, line.size)
        else:
            models.Product.increase_other_stock(product.id, quantity)
        models.OrderLine.remove_order_line(line_id)
        models.Order.update_order_total(g.current_order.id)
        flash("Item removed", "success")
        return redirect(url_for('basket', user_id=current_user.id))


@app.route('/checkout')
@login_required
def checkout():
    if g.current_order.order_lines.count() == 0:
        flash("No items to checkout", "error")
        return redirect(url_for('products'))
    elif g.default_address is not None:
        return render_template("checkout.html", current_basket=g.current_basket,
                               current_order=g.current_order, default_address=g.default_address)
    else:
        flash("Please add delivery address", "error")
        session["checking out"] = True
        return redirect(url_for("add_address"))


@app.route('/')
def index():
    """Route that returns the index(home) page"""
    return render_template('index.html', current_basket=g.current_basket, user=current_user)


@app.errorhandler(404)
def not_found(error):
    """Route that returns a custom 404 page if the user encounters that error"""
    return render_template('404.html', current_basket=g.current_basket, current_order=g.current_order)


# if the app is being run directly, rather than imported
if __name__ == '__main__':
    # run the initialize method in models to create tables if they don't exist
    models.initialize()

    # creates base admin user
    try:
        models.User.create_user(
            first_name="Admin",
            last_name="User",
            email_address="contact@nativesins.com",
            password="password",
            user_role="admin"
        )
    except ValueError:
        pass

    app.run(host='localhost', debug=True, port=5000)
