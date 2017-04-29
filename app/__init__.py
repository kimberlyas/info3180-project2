from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './app/static/uploads' # location where file uploads will be stored
app.config['SECRET_KEY'] = os.urandom(24) # used for session security
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://admin:password@localhost/project2" # database setup
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True # added just to suppress a warning

# Set up Flask-SQLAlchemy
db = SQLAlchemy(app)

app.config.from_object(__name__)
from app import views

