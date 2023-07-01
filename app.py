
from SV import create_app
from SV.users.forms import LoginForm
from flask_login import login_user
from flask import request
from flask import render_template, redirect, url_for
from SV.models import User
from flask_login import logout_user, login_required

import sys

app         = create_app('flask.cfg')


class NConnections():
    """
    Class representing the number of connections.

    Attributes:
        n_con (int): The number of connections.

    Methods:
        query: Increments the number of connections by 1 and returns the updated value.
    """
    def __init__(self, n_con):
        """
        Initialize the NConnections object.

        Args:
            n_con (int): The initial number of connections.
        """
        self.n_con = n_con

    def query(self):
        """
        Increments the number of connections by 1 and returns the updated value.

        Returns:
            int: The updated number of connections.
        """
        self.param += 1
        return self.param


obj_n_connections = NConnections(0) 



@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Route for the login page.

    If the form is submitted and valid:
        - Fetch the user from the User Models table based on the email address.
        - Verify the password for the user.
        - Log in the user if the password is correct.
        - Redirect to the next page or the welcome page.

    Returns:
        A rendered template for the login page.
    """
    print('Logging in. . .')
    form = LoginForm()

    if form.validate_on_submit():
        # Grab the user from our User Models table
        user = User.query.filter_by(email=form.email.data).first()

        # Check that the user was supplied and the password is right
        # The verify_password method comes from the User object
        # https://stackoverflow.com/questions/2209755/python-operation-vs-is-not

        if user is None:
            print('User is None')
            return render_template('login.html', form = form, log_error = True)
        elif user.check_password(form.password.data) and user is not None:
            # Log in the user

            login_user(user)
            # If a user was trying to visit a page that requires a login
            # flask saves that URL as 'next'.
            next = request.args.get('next')

            # So let's now check if that next exists, otherwise we'll go to
            # the welcome page.
            if next == None or not next[0] == '/':
                next = url_for('page_all.welcome_user')

            print("Next: ", next)
            return redirect(next)
    return render_template('login.html', form=form, log_error = False)


@app.route('/logout')
@login_required
def logout():
    """
    Route for logging out the user.

    Returns:
        Redirects to the home page.
    """

    logout_user()
    return redirect(url_for('page_all.home'))


if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', debug=False)
    except OSError as e:
        if e.errno == 98:
            print('Port 5000 is already in use. Trying a different port...', file=sys.stderr)
            app.run(host='0.0.0.0', debug=True, port=5001)
        else:
            raise e