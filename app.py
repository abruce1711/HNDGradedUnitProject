from flask import (Flask, g, render_template, flash, redirect, url_for, abort, request)
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import check_password_hash

import forms
import models

app = Flask(__name__)
app.secret_key = "dvapvhsdfbvasoifjsfobmskdfnv394t5e943i-4"

login_manager = LoginManager(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(userid):
    try:
        return models.User.get(models.User.id == userid)
    except models.DoesNotExist:
        return None


@app.before_request
def before_request():
    """Connect to the database before each request"""

    g.db = models.db
    g.db.connect()
    g.user = current_user


@app.after_request
def after_request(response):
    """Close database connection after each request"""
    g.db.close()
    return response


@app.route('/login', methods=('GET', 'POST'))
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        try:
            user = models.User.get(models.User.email_address == form.email_address.data)
        except models.DoesNotExist:
            flash("Email or password incorrect", "error")
        else:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                flash("Log in successful", "success")
                return redirect(url_for('index'))
            else:
                flash("Email or pasword incorrect", "error")
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out", "success")
    return redirect(url_for('login'))

@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    models.initialize()

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
