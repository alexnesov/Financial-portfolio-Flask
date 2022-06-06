from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


db                          = SQLAlchemy()
login_manager               = LoginManager()
# login_manager.init_app()
login_manager.login_view    = "login"



# Using the Application factory pattern to create the Flask application
# https://flask.palletsprojects.com/en/2.0.x/patterns/appfactories/
# https://testdriven.io/blog/flask-pytest/

######################################
#### Application Factory Function ####
######################################

def create_app(config_filename=None):

    print(f"config_filename: {config_filename}")
    app = Flask(__name__, static_url_path='/static', instance_relative_config=True)
    app.config.from_pyfile(config_filename)
    initialize_extensions(app)

    return app


##########################
#### Helper Functions ####
##########################

def initialize_extensions(app):
    # Since the application instance is now created, pass it to each Flask
    # extension instance to bind it to the Flask application instance (app)
    db.init_app(app)
    login_manager.init_app(app)

    # Flask-Login configuration
    from SV.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.filter(User.id == int(user_id)).first()

