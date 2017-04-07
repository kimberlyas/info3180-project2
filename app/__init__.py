from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_jwt import JWT
#from flask.ext.security import Security, SQLAlchemyUserDatastore 
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './app/static/uploads' # location where file uploads will be stored
app.config['SECRET_KEY'] = os.urandom(24) # used for session security
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://admin:password@localhost/project2" # database setup
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True # added just to suppress a warning
#app.config['JWT_EXPIRATION_DELTA'] = # token expires in 
app.config['JWT_AUTH_ENDPOINT'] = 'Bearer' # authorization header

db = SQLAlchemy(app)

import models

# Setup Flask-JWT
jwt = JWT(app, models.authenticate, models.identity)

# Setup Flask-Security
# user_datastore = SQLAlchemyUserDatastore(db, UserProfile, Wish)
# security_manager = Security(app, user_datastore)

# Flask-Login login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

app.config.from_object(__name__)
from app import views

