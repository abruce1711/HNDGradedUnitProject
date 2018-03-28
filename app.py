from flask import Flask

import models

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


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
    except ValueError as e:
        print(e)

    app.run(host='localhost', debug=True, port=5000)
