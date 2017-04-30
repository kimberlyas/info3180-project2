from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './app/static/uploads' # location where file uploads will be stored
app.config['SECRET_KEY'] = os.urandom(24) # used for session security
#app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://admin:password@localhost/project2" # database setup
#DATABASE_URL='postgres://rytmloidwripgk:1f1c20a3b1e7b951b95b07cbc375903f9d16ddc6225789b82c097c6f64265385@ec2-54-235-168-152.compute-1.amazonaws.com:5432/d35ul9km490k63'
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://rytmloidwripgk:1f1c20a3b1e7b951b95b07cbc375903f9d16ddc6225789b82c097c6f64265385@ec2-54-235-168-152.compute-1.amazonaws.com:5432/d35ul9km490k63" # database setup
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True # added just to suppress a warning

# Set up Flask-SQLAlchemy
db = SQLAlchemy(app)

app.config.from_object(__name__)
from app import views

