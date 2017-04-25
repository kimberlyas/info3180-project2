"""
Flask Documentation:     http://flask.pocoo.org/docs/
Jinja2 Documentation:    http://jinja.pocoo.org/2/documentation/
Werkzeug Documentation:  http://werkzeug.pocoo.org/documentation/
This file creates your application.
"""

from app import app, db, login_manager
from flask import render_template, request, redirect, url_for, flash, jsonify, json, send_from_directory, make_response, abort
from flask_login import login_user, logout_user, current_user, login_required
from flask_jwt import JWT, jwt_required, current_identity
from sqlalchemy.sql import text
from werkzeug.utils import secure_filename
from forms import LoginForm, SignupForm
from models import UserProfile, Wish, users_wishes
from bs4 import BeautifulSoup
import requests
import urlparse
import time
import os
import random

###
# JWT Handlers
###
def authenticate(email,password):
    """ Returns an authenticated identity """
    # Lookup user
    user = UserProfile.query.filter_by(email=email).first()
    if not user:
        abort(404) # not found
    # Validate user's password
    if user.check_password(password):
        # Return the user object
        return user
    else:
        abort(401) # unauthorized

def identity(payload):
    """ Returns a user given an existing token """
    return UserProfile.query.get(payload['identity'])
    
def auth_response_handler(access_token, identity):
    """ Custom token response """
    #Set error boolean
    err = None
    # Set message field
    msg = "Success"
    # Create data dict
    userData = {'email': identity.email, 'name': identity.name}
    jsonData = {'user': userData, 'access_token': access_token.decode('utf-8'), 'payload': jwt.jwt_payload_callback()}
    
    # Generate JSON object
    return jsonify(error=err, data=jsonData, message=msg), 302 # found

## Setup Flask-JWT
jwt = JWT(app, authenticate, identity)
        
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

# # EXTRA - add profile page for users (DEFER TO FRONT-END)
# @app.route('/api/users/<int:userid>', methods=['GET'])
# def view_profile(userid):
#     """ Render an individual user profile page """
    
#     # Search for given userid
#     user_profile = UserProfile.query.filter_by(id=userid).first()
#     # Check if found
#     if user_profile is not None:
        
#         # Render user's profile page
#         return render_template('view_profile.html', user_profile=user_profile)
    
#     else: # Not found
        
#         # Flash error message
#         flash('Sorry! User does not exist.','danger')
            
#         # Redirect to home
#         return redirect(url_for('home'))
           
# ADMIN Test 1        
@app.route("/api/users/<int:userid>", methods=['GET'])  
def get_user(userid):
    """ Returns a user's profile as a JSON object"""
    # Search for userid
    user = UserProfile.query.get(userid)
    # Check if not found
    if not user:
        # Error
        abort(404) # resource not found
    # Return user info as JSON output
    err = None
    msg = "Success"
    userData = {'id':user.id, 'email': user.email,'name': user.name, 'password': user.password, 'age': user.age, 'gender': user.gender, 'image': user.image}
    # Generate JSON output
    return jsonify(error=err, data={'user': userData}, message=msg)

# ADMIN Test 2
@app.route("/api/items/<int:itemid>")  
def get_item(itemid):
    """ Returns a wishlist item """
    # Search for itemid
    wish = Wish.query.get(itemid)
    # Check if not found
    if not wish:
        # Error
        abort(404)
    # Return wish info as JSON output
    err = None
    msg = "Success"
    itemData = {'id': wish.item_id, 'title': wish.title, 'description': wish.description, 'url': wish.url, 'thumbnail_url': wish.thumbnail}
    # Generate JSON output
    return jsonify(error=err, data={'item': itemData}, message=msg)

# NEEDS SOME WORK (ADMIN Test 3)
@app.route("/api/token/<user>")
def authorize_user(user):
    """ Generates a token header for a user """
    # Return Format --> Authorization: <token schema> <token>
    auth = 'Bearer ' + encode_user(user)
    return requests.post(url_for("login", _external=True), headers={'Authorization': auth})

###
# Share Feature (GEORGIA)
###
@app.route("/share/<int:userid>/wishlist")
def share_wishlist(): 
    """ Allows a user to share their wishlist with friends or family via email"""
    pass 
    

###
# API Routes
###
@app.route("/api/users/register", methods=["POST"])
def signup():
    """ Accepts user information and saves it to the database """
    # Check for JSON object
    if not request.json:
        abort(400)
    
    # Get JSON data values
    name = request.json['name']
    
    ## EMAIL FIELD
    email = request.json['email']
    # Check if email has been used before
    if UserProfile.query.filter_by(email = email).first() is not None:
        return jsonify(error=True, data=None, message="Email already in use"), 400 # existing user
    
    password = request.json['password']
    
    # Check manadatory json fields
    if name is None or email is None or password is None:
        abort(400) # missing arguments
    
    # Get other fields
    age = request.json['age']
    gender = request.json['gender']
    
    ## IMAGE FIELD
    # Uploads folder
    imageFolder = app.config["UPLOAD_FOLDER"]
    # Store default profile pic in DB
    imageName = "profile-default.gif"
    # Get picture file
    if 'image' in request.files: # tolerate missing image
        imageFile = request.files['image'] 
        # Secure file
        imageName = secure_filename(imageFile.filename)
        # Save to uploads directory
        imageFile.save(os.path.join(imageFolder, imageName))
    
    ## ID FIELD        
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
        
    ## DATE FIELD
    # Generate the date the user was created on
    created_on = timeinfo()
    
    # Create user object
    user = UserProfile(userid,name,age,gender,imageName,email,password,created_on)
    # Store data in database
    db.session.add(user)
    db.session.commit()
    
    # Set up JSON response
    err = None
    msg = "Success"
    userData = {'id': user.id, 'email': user.email,'name': user.name, 'age': user.age, 'gender': user.gender, 'image': user.image, 'uri': url_for('get_user', userid = user.id, _external = True)}
    # Generate JSON output
    return jsonify(error=err, data={'user': userData}, message=msg), 201 # user created
    

@app.route("/api/users/login", methods=["POST"])
def login():
    """ Accepts login credentials as email and password """
    
    # Store authorization request
    auth = request.json
    
    # Check for json header
    if not auth:
        abort(400) # bad request
        
    # Get data fields
    email = auth['email']
    password = auth['password']
        
    # Check fields
    if email is None or password is None:
        abort(400) # missing arguments
        
    # Check authentication
    identity = jwt.authentication_callback(email, password)
            
    # Generate an access token
    access_token = jwt.jwt_encode_callback(identity)
            
    # Generate json response
    return jwt.auth_response_handler(access_token, identity)
        
@app.route("/api/users/<int:userid>/wishlist", methods=["GET","POST"])
@jwt_required()
def view_wishlist(userid):
    """ Returns a user's wishlist """
    
    # Seach for user whose wishlist we'd like to view
    user = db.session.query(UserProfile).filter_by(id=userid).first()
    
    # Check request type
    if request.method == "GET": # View user's wishlist
        
        # Check if user was found
        if user:
            
            # Initialize list of wishes
            wishList = []
            
            # Define SQL query
            query = text("""SELECT wish.item_id, wish.title, wish.description, wish.url, wish.thumbnail FROM wish INNER JOIN users_wishes ON users_wishes.wish_id = wish.item_id WHERE users_wishes.user_id = :id""")
            # Get all items in specific user's wishlist
            wishes = db.session.get_bind().execute(query, id=user.id)
            
            # Check if there were any wishes
            if wishes:
            
                # Get each wish
                for wish in wishes:
                    # Create dictionary format
                    wishDict = {'id': wish["item_id"], 'title': wish["title"], 'description': wish["description"], 'url': wish["url"], 'thumbnail_url': wish["thumbnail"]}
                    # Add to list of wishes
                    wishList.append(wishDict)
            
                # JSON
                err = None
                msg = "Success"
                userData = {"items": wishList}
            else: # No wishes found
                # Error?
                err = True
                msg = "No wishes found"
                userData = {"items": wishList}
        else: # No such user found
            # Error
            abort(404)
        
        # Generate JSON object
        return jsonify(error=err, data=userData, message=msg)
                
    elif request.method == "POST": # Add item to wishlist
    
        # Get JSON object from Angular Server
        if request.json:
            jsonObj = request.json
        else:
            abort(400) # bad request
        
        # Get fields
        title = jsonObj['title']
        description = jsonObj['description']
        url = jsonObj['url']
        thumbnail_url = jsonObj['thumbnail_url']
        
        # Check fields
        if title is None or description is None or url is None or thumbnail_url is None:
            abort(400) # missing arguments
        
        # Check if user was found
        if user:
            # Create Wish object
            wish = Wish(title,description,url,thumbnail_url)
            # Save to DB
            db.session.add(wish)
            # Commit changes
            db.session.commit()
            # Add entry to relationship table
            db.session.get_bind().execute(users_wishes.insert(), user_id=userid, wish_id=wish.item_id)
            # JSON
            err = None
            itemData = {'id': wish.item_id, 'title': wish.title, 'description': wish.description, 'url': wish.url, 'thumbnail_url': wish.thumbnail, 'uri': url_for('get_item', itemid = wish.item_id, _external = True), 'current_identity': str(current_identity)}
            msg = "Success"
        else:
            # User not found
            abort(404)
    
        # Generate JSON object
        return jsonify(error=err, data={'item': itemData}, message=msg), 201 # created
        

@app.route("/api/users/<int:userid>/wishlist/<int:itemid>", methods=["DELETE"])
@jwt_required()
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
            err = None
            msg = "Success"
            userData = {'itemid': wish.item_id, 'title': wish.title}
        else: # Wish not found
            # Error
            abort(404)
    else: # User not found
        # Error
        abort(404)
    
    # Generate JSON object
    return jsonify(error=err, data=userData, message=msg)    
            

@app.route('/api/thumbnails', methods=['GET'])
def get_thumbnails():
    """ Accepts a URL and returns JSON containing a list of thumbnails """
    # Check for json Object
    if not request.json or 'url' not in request.json:
        abort(400)
    # Get URL
    url = request.json['url']
    # Get image URLs
    urls = get_imageURLS(url)
    # Generate JSON output
    if urls:
        err = None
        msg = "Success"
    else:
        err = True
        msg = "URL request error"
    
    return jsonify(error=err, data={'thumbnails': urls}, message=msg)
    


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
def serve_file(filename):
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
    response. headers['Cache-Control'] = 'public, max-age=0'
    return response

# # send CORS headers
# @app.after_request
# def after_request(response):
#     response.headers.add('Access-Control-Allow-Origin', '*')
#     if request.method == 'OPTIONS':
#         response.headers['Access-Control-Allow-Methods'] = 'DELETE, GET, POST, PUT'
#         headers = request.headers.get('Access-Control-Request-Headers')
#         if headers:
#             response.headers['Access-Control-Allow-Headers'] = headers
#     return response
    
@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    if request.headers['Content-Type'] == 'application/json':
        err = True
        msg = "Not found"
        appData = None
        return make_response(jsonify(error=err, data=appData, message=msg), 404)
    else:
        return render_template('404.html'), 404

@app.errorhandler(400)
def bad_request(error):
    err = True
    msg = "Bad request"
    appData = None
    return make_response(jsonify(error=err, data=appData, message=msg), 400)

@app.errorhandler(401)
def unauthorized_access(error):
    err = True
    msg = "Unauthorized Access"
    appData = None
    return make_response(jsonify(error=err, data=appData, message=msg), 401)
    
if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0",port="8080")
