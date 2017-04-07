"""
Flask Documentation:     http://flask.pocoo.org/docs/
Jinja2 Documentation:    http://jinja.pocoo.org/2/documentation/
Werkzeug Documentation:  http://werkzeug.pocoo.org/documentation/
This file creates your application.
"""

from app import app, db, login_manager, jwt
from flask import render_template, request, redirect, url_for, flash, jsonify, send_from_directory, session
from flask_login import login_user, logout_user, current_user, login_required
from flask_jwt import jwt_required, current_identity
from sqlalchemy.sql import text
from werkzeug.utils import secure_filename
from forms import LoginForm, SignupForm
from models import UserProfile, Wish
from bs4 import BeautifulSoup
import requests
import urlparse
import time
import os
import random


###
# Routing for your application.
###

@app.route('/')
def home():
    """Render website's home page."""
    return render_template('home.html')

@app.route('/about/')
def about():
    """Render the website's about page."""
    return render_template('about.html')

# user_loader callback. This callback is used to reload the user object from
# the user ID stored in the session
@login_manager.user_loader
def load_user(id):
    return UserProfile.query.get(int(id))
    
@app.route("/logout")
@login_required
def logout():
    # logout user and end session
    logout_user()
    # flash message to user
    flash('Logged out.', 'danger')
    # redirect to the home route
    return redirect(url_for('home'))

# send CORS headers
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    if request.method == 'OPTIONS':
        response.headers['Access-Control-Allow-Methods'] = 'DELETE, GET, POST, PUT'
        headers = request.headers.get('Access-Control-Request-Headers')
        if headers:
            response.headers['Access-Control-Allow-Headers'] = headers
    return response

# GEORGIA
@app.route("/share/<userid>/wishlist")
def share_wishlist(): 
    """ Allows a user to share their wishlist with friends or family via email"""
    pass 
    # Can use Flask-Mail?? :/

###
# API Routes
###
@app.route("/api/users/register", methods=["GET","POST"])
def signup():
    """ Accepts user information and saves it to the database """
    # Generate sign up form
    form = SignupForm()
    # Check request type
    if request.method == "POST":
        # Validate form
        if form.validate_on_submit():
            # Get form values
            name = request.form['name']
            email = request.form['email']
            password = request.form['password']
            age = request.form['age']
            gender = request.form['gender']
            # Uploads folder
            imageFolder = app.config["UPLOAD_FOLDER"]
            # Get picture file
            imageFile = request.files['image']
            # Check if empty
            if imageFile.filename == '':
                # Store default profile pic in DB
                imageName = "profile-default.gif"
            else:
                # Secure file
                imageName = secure_filename(imageFile.filename)
                # Save to uploads directory
                imageFile.save(os.path.join(imageFolder, imageName))
            
            # Loop to find a unique id
            while True:
                # Generate a random userid
                userid = random.randint(620000000, 620099999)
                # Search for this userid
                result = UserProfile.query.filter_by(id=userid).first() 
                # Check if not found
                if result is None:
                    # Unique; Exit loop
                    break
            # Generate the date the user was created on
            created_on = timeinfo()
            # Create user object
            user = UserProfile(userid,name,age,gender,imageName,email,password,created_on)
            # Store data in database
            db.session.add(user)
            db.session.commit()
            # Set up JSON response
            err = False
            msg = "Success"
            userData = {'email': user.email,'name': user.name, 'password': user.password, 'age': user.age, 'gender': user.gender, 'image': user.image}
        
        else:
            # Error
            err = True
            # Error Message
            msg = form.errors
            # Set data property
            userData = None
        
        # Generate JSON output
        return jsonify(error=err, data=userData, message=msg)
                        
    # Display any errors in form
    flash_errors(form)
    
    # Load registration page
    return render_template("signup.html", form=form)

@app.route("/api/users/login", methods=["GET", "POST"])
def login():
    """ Accepts login credentials as email and password """
    # Generate login form
    form = LoginForm()
    # Check request type
    if request.method == "POST":
        # Validate form submission
        if form.validate_on_submit():
            # Get the email and password values from the form
            email = form.email.data
            password = form.password.data
            
            # Query database for a user based on the email submitted
            user = UserProfile.query.filter_by(email=email).first()
            
            # Check if user was found and if password matches stored pswd value
            if user is not None and user.check_password(password):
                # Set error boolean
                err = False
                # Set message field
                msg = "Success"
                # Create user dict
                userData = {'email': user.email, 'password': user.password}
            else:
                # Error 
                err = True
                # Error Message
                msg = "Invalid username/password"
                # Data property
                userData = user # empty object
        else:
            # Set error property
            err = True
            # Leave data property as an empty object
            userData = None
            # Set appropriate error message
            msg = form.errors
        
        # Generate JSON object
        return jsonify(error=err, data=userData, message=msg)
    
    # Display any errors in form
    flash_errors(form)
    
    # Load login page
    return render_template("login.html", form=form)

@app.route("/api/users/<userid>/wishlist", methods=["GET","POST"])
@jwt_required()
@login_required
def view_wishlist(userid):
    """ Renders user's wishlist """
    
    # Seach for user whose wishlist we'd like to view
    user = db.session.query(UserProfile).filter_by(id=userid).first()
    
    # Check request type
    if request.method == "GET":
        
        # Check if user was found
        if user:
            # Define SQL query
            query = text("""SELECT wish.item_id, wish.title, wish.description, wish.url, wish.thumbnail  
                                       FROM user_profile JOIN users_wishes JOIN wish 
                                       ON user_profile.id = users_wishes.user_id AND users_wishes.wish_id = wish.item_id 
                                       WHERE user_profile.id = :id""")
            # Get all items in specific user's wishlist
            wishes = db.execute(query, **user)
            
            # Check if there were any wishes
            if wishes:
            
                # Initialize list of wishes
                wishList = []
            
                # Get each wish
                for wish in wishes:
                    # Create dictionary format
                    wishDict = {'id': wish.item_id, 'title': wish.title, 'description': wish.description, 'url': wish.url, 'thumbnail_url': wish.thumbnail}
                    # Add to list of wishes
                    wishList.append(wishDict)
            
                # JSON
                err = False
                msg = "Success"
                userData = {"wishes":wishList}
            else: # No wishes found
                # Error?
                err = True
                msg = "No wishes found"
                userData = {}
        else: # No such user found
            # Error
            err = True
            msg = "User not found"
            userData = None
                
    elif request.method == "POST":
    
        # Get JSON object from Angular Server
        jsonObj = request.json
        
        # Check if user was found
        if user:
            # Create Wish object
            wish = Wish(title=jsonObj['title'], description=jsonObj['description'], url=jsonObj['url'] ,thumbnail=jsonObj['thumbnail'])
            # Save to DB
            db.session.add(wish)
            db.session.commit()
            # JSON
            err = False
            userData = {'title': wish.title, 'description': wish.description, 'url': wish.url, 'thumbnail_url': wish.thumbnail}
            msg = "Successfully saved"
        else:
            # Set error property
            err = True
            # Set error message
            msg = "User not found"
            # Empty object
            userData = None
    
        # Generate JSON object
        return jsonify(error=err, data=userData, message=msg)
        
    return render_template('wishlist.html', wishlist=wishes)

@app.route("/api/users/<userid>/wishlist/<itemid>", methods=["DELETE"])
@jwt_required()
@login_required
def delete_item(userid, itemid):
    """ Deletes an item from a user's wishlist """
    
    # Seach for user whose wishlist we'd like to view
    user = db.session.query(UserProfile).filter_by(id=userid).first()
    # Check if user was found
    if user:
        # Get specified item
        wish = db.session.query(Wish).filter_by(item_id=itemid).first()
        # Check if item was found
        if wish:
            # Delete from DB
            db.session.delete(wish)
            # Save changes
            db.session.commit()
            # JSON
            err = False
            msg = "Success"
            userData = {'itemid': wish.item_id}
        else: # Wish not found
            # Error
            err = True
            msg = "Wished Item not found"
            userData = {}
    else: # User not found
        # Error
        err = True
        msg = "User not found"
        userData = None
    
    # Generate JSON object
    return jsonify(error=err, data=userData, message=msg)    
            

@app.route('/api/thumbnails', methods=['GET'])
def get_thumbnails(url):
    """ Accepts a URL and returns JSON containing a list of thumbnails """
    # Get image URLs
    urls = get_imageURLS(url)
    # Generate JSON output
    if urls:
        err = None
        msg = "Success"
    else:
        err = "Request Error"
        msg = "Failed"
    
    return jsonify(error=err, data=urls, message=msg)

###
# The functions below should be applicable to all Flask apps.
###

def timeinfo():
    """ Returns the current datetime """
    return time.strftime("%d %b %Y")

def flash_errors(form):
    """Flashes form errors"""
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error ), 'danger')

def get_imageURLS(url):
    """ Returns a list of thumbnail URLS """
    result = requests.get(url)
    soup = BeautifulSoup(result.text, "html.parser")

    # This will look for a meta tag with the og:image property
    og_image = (soup.find('meta', property='og:image') or
                    soup.find('meta', attrs={'name': 'og:image'}))
    if og_image and og_image['content']:
        pass

    # This will look for a link tag with a rel attribute set to 'image_src'
    thumbnail_spec = soup.find('link', rel='image_src')
    if thumbnail_spec and thumbnail_spec['href']:
        pass

	# Return a list of image URLs
    imgs = [] 
    for img in soup.findAll("img", src=True):
        
        imgs.append(urlparse.urljoin(url, img["src"]))
        
    return imgs

@app.route('/img/<path:filename>')
def serve_file(path):
    dir = app.config["UPLOADS_FOLDER"]
    return send_from_directory(dir,filename)

@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)

@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0",port="8080")
