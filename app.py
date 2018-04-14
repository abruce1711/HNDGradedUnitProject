# all imports for the app to work
from flask import (Flask, g, render_template, flash, redirect, url_for, abort, request)
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
        return redirect(url_for('login'))
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
        return render_template('create_user.html', form=form)


@app.route('/create_product', methods=('GET', 'POST'))
@login_required
def create_product():
    form = forms.CreateProduct()

    if current_user.user_role == "customer":
        abort(404)
    else:
        if form.validate_on_submit():
            if form.product_size.data == '':
                flash("Must select size", "error")
            else:
                models.Product.create_product(
                    name=form.product_name.data,
                    category=form.product_category.data,
                    size=form.product_size.data,
                    price=form.product_size.data,
                    description=form.product_description.data,
                    stock=form.product_stock_level.data
                )
                flash("Product Created", "success")
                return redirect(url_for('create_product'))
        return render_template('create_product.html', form=form)


@app.route('/')
def index():
    """Route that returns the index(home) page"""
    return render_template('index.html')


@app.errorhandler(404)
def not_found(error):
    """Route that returns a custom 404 page if the user encounters that error"""
    return render_template('404.html')


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
