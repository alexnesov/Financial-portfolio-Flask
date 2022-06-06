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
    register_blueprints(app)

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



def register_blueprints(app):
    # Since the application instance is now created, register each Blueprint
    # with the Flask application instance (app)
    from app_all import page_all
    from app_macro import page_macro
    from app_signals import page_signals

    app.register_blueprint(page_all)
    app.register_blueprint(page_macro)
    app.register_blueprint(page_signals)
