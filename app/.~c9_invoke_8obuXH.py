"""
Flask Documentation:     http://flask.pocoo.org/docs/
Jinja2 Documentation:    http://jinja.pocoo.org/2/documentation/
Werkzeug Documentation:  http://werkzeug.pocoo.org/documentation/
This file creates your application.
"""

from app import app, db
from flask import render_template, request, redirect, url_for, flash, jsonify, json, send_from_directory, make_response, abort
from flask_jwt import JWT, jwt_required, current_identity
from sqlalchemy.sql import text
from werkzeug.datastructures import ImmutableMultiDict
from werkzeug.utils import secure_filename
from models import UserProfile, Wish, users_wishes
from bs4 import BeautifulSoup
import requests
import urlparse
import time
import os
import random
import datetime
import share # Send email feature

###
# JWT Handlers
###
app.config['JWT_EXPIRATION_DELTA'] = datetime.timedelta(seconds=86400) # token expires in timedelta(seconds=300) currently (5 mins) change to a day
app.config['JWT_AUTH_ENDPOINT'] = 'bearer' # authorization header
app.config['JWT_AUTH_HEADER_PREFIX'] = 'BEARER' # OAuth2 Bearer tokens

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
    jsonData = {'user': userData, 'access_token': access_token.decode('utf-8'), 'payload': jwt.jwt_payload_callback(identity)}
    
    # Generate JSON object
    return jsonify(error=err, data=jsonData, message=msg)

## Setup Flask-JWT
jwt = JWT(app, authenticate, identity)
        
###
# Routing for your application.
###

@app.route('/app')
def wishListApp():
    """ Load website's main page."""
    # This loads a static HTML file where we then hand over the interaction
    # to AngularJS
    return app.send_static_file('index.html')

@app.route('/')
def home():
    """Render website's home page."""
    return render_template('home.html')

@app.route('/about/')
def about():
    """Render the website's about page."""
    return render_template('about.html')
    
###
# Share Feature (GEORGIA)
###
@app.route("/api/users/<int:userid>/shareWishlist", methods=["GET","POST"])
def share_wishlist(userid): 
    """ Allows a user to share their wishlist with friends or family via email"""
    
    # Get user
    user = db.session.query(UserProfile).filter_by(id=userid).first()
    
    # Check request method
    if request.method == "POST":
        # Initialize mailing list
        emails = []
        # Check for json data
        if request.json:
            # Get json data
            json_data = request.json
        else:
            # Error - bad request
            abort(400) 
       
        # Check if user was found
        if user:
            # Check for emails
            if 'email1' in json_data:
                # Append to mailing list
                emails.append(json_data['email1'])
            
            if 'email2' in json_data:
                emails.append(json_data['email2'])
                
            if 'email3' in json_data:
                emails.append(json_data['email3'])
            
            if 'email4' in json_data:
                emails.append(json_data['email4'])
            
            if 'email5' in json_data:
                emails.append(json_data['email5'])
                
            # Check that at least one email was received
            if not emails:
                # Empty mailing list
                abort(400) # missing arguments
            
            # Get sending details
            from_name = user.name
            from_addr = user.email
            subject = "My Favourite Things"
            # This link may change (heroku)
            link = "\n\nhttps://info3180-project2-kimberlyas.c9users.io/app#/wishList/" + str(user.id)
            msg = "Good Day Family and Friends! \n\nI would love to get these items! Any item you can purchase will be greatly appreciated :) " + "" + link
        
            # Iterate through mailing list
            for email in emails:
                # Send email to receiver
                share.sendemail(email,from_addr,from_name,subject,msg)
            
            # Generate json
            shareData = {'sent_to': emails}
            response = jsonify({"error":None,"data":shareData,"message":"Success"})
            return response
            
        else: # user not found
            abort(404)
    elif request.method == "GET": # return specific shared wishlist
        
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
                userData = {"items": wishList, "user": user.name}
            else: # No wishes found
                # Error?
                err = True
                msg = "No wishes found"
                userData = {"items": wishList, "user": user.name}
            
            # Generate JSON object
            return jsonify(error=err, data=userData, message=msg)
            
        else: # user not found
            abort(404)
    
###
# API Routes
###
@app.route("/api/users/register", methods=["POST"])
def signup():
    """ Accepts user information and saves it to the database """
    
    data = None;
    
    if request.form:
        data = request.form
    elif request.json:
        data = request.json
    
    # if request.headers['Content-Type'] == 'multipart/form-data' or request.headers['Content-Type'] == 'undefined':
    #     data = dict(request.form)
    # elif request.json:
    #     data = request.json
    
    # data = request.json
        
    # Check for JSON object
    if not data:
        abort(400)
    
    # Check manadatory json fields
    if 'name' not in data or 'email' not in data or 'password' not in data:
        abort(400) # missing arguments
        
    # Get JSON data values
    name = data['name']
    
    ## EMAIL FIELD
    email = data['email']
    # Check if email has been used before
    if UserProfile.query.filter_by(email = email).first() is not None:
        return jsonify(error=True, data={}, message="Email already in use"), 400 # existing user
    
    password = data['password']
    
    # Tolerate missing other fields
    if 'age' in data:
        age = data['age']
    else:
        age = None
    
    if 'gender' in data:
        gender = data['gender']
    else:
        gender = None
    
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
    userData = {'id': user.id, 'email': user.email,'name': user.name, 'age': user.age, 'gender': user.gender, 'image': user.image, 'created_on': user.created_on, 'uri': url_for('get_user', userid = user.id, _external = True)}
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
        
    # Check fields
    if 'email' not in auth or 'password' not in auth:
        abort(400) # missing arguments
        
    # Get data fields
    email = auth['email']
    password = auth['password']
        
    # Check authentication
    identity = jwt.authentication_callback(email, password)
            
    # Generate an access token
    access_token = jwt.jwt_encode_callback(identity)
            
    # Generate json response
    return auth_response_handler(access_token, identity)
        
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
        
        # Check fields
        if 'title' not in jsonObj or 'description' not in jsonObj or 'url' not in jsonObj or 'thumbnail_url' not in jsonObj:
            abort(400) # missing arguments
       
        # Get fields
        title = jsonObj['title']
        description = jsonObj['description']
        url = jsonObj['url']
        thumbnail_url = jsonObj['thumbnail_url']
        
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
            itemData = {'id': wish.item_id, 'title': wish.title, 'description': wish.description, 'url': wish.url, 'thumbnail_url': wish.thumbnail, 'uri': url_for('get_item', itemid = wish.item_id, _external = True)}
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
            itemData = {'itemid': wish.item_id, 'title': wish.title}
        else: # Wish not found
            # Error
            abort(404)
    else: # User not found
        # Error
        abort(404)
    
    # Generate JSON object
    return jsonify(error=err, data={'item': itemData}, message=msg)    
            

@app.route('/api/thumbnails', methods=['GET'])
def get_thumbnails():
    """ Accepts a URL and returns JSON containing a list of thumbnails """
    
    print request.json()
    print request.GET['url'] # for GET form method
    # Check for json Object
    if not request.json:
        abort(400) # bad request
    
    # Get URL
    if 'url' in request.json:
        url = request.json['url']
    else:
        abort(400) # bad request
        
    # Get image URLs
    urls = get_imageURLS(url)
    # Generate JSON output
    if urls:
        err = None
        msg = "Success"
    else:
        err = True
        msg = "Unable to extract thumbnails"
    
    return jsonify(error=err, data={'thumbnails': urls}, message=msg)
    
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
    userData = {'id':user.id, 'email': user.email,'name': user.name, 'password': user.password, 'age': user.age, 'gender': user.gender, 'image': user.image, 'created_on': user.created_on}
    # Generate JSON output
    return jsonify(error=err, data={'user': userData}, message=msg)

# ADMIN Test 2
@app.route("/api/items/<int:itemid>", methods=['GET'])  
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

# # ADMIN Test 3 - Testing JWT features
# @app.route("/api/token/<int:userid>", methods=['GET'])
# def authorize_user(userid):
#     """ Generates a token header for a user """
#     # Return Format --> Authorization: <token schema> <token>
#     # Get resource
#     resource = request.json['resource']
#     # Search for userid
#     user = UserProfile.query.get(userid)
#     # Check if found
#     if user:
#       # Create header 
#       auth = 'Bearer ' + str(jwt.jwt_encode_callback(user))
#       headers = 'Authorization' + auth
      
#       # Create json response
#       err = None
#       msg = "Success"
#       tokenData = {'headers': str(jwt.jwt_headers_handler(user)), 'auth': headers, 'current_identity': str(current_identity), 'payload': jwt.jwt_payload_handler(user), 'url': headers + url_for(resource,userid=user.id,_external=True) }
#       return jsonify(error=err, data={'token': tokenData}, message=msg)
#       #return requests.post(url_for("login", _external=True), headers={'Authorization': auth})
#     else:
#         abort(404) # not found

###
# The functions below should be applicable to all Flask apps.
###
def timeinfo():
    """ Returns the current datetime """
    return time.strftime("%d %b %Y")

def get_imageURLS(url):
    """ Returns a list of thumbnail URLS """
    try:
        result = requests.get(url)
    except Exception:
        # Error
        abort(500)
        
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
    
    #if request.headers['Content-Type'] == 'application/json':
    err = True
    msg = "Not found"
    appData = {} # empty object
    return make_response(jsonify(error=err, data=appData, message=msg), 404)
    #else:
        
#     if os.environ.haskey("If-Modified-Since"):
         #return render_template('404.html'), 404
      #el
#   # do something with the header, i.e. os.environ["SOME_HEADER"]

@app.errorhandler(400)
def bad_request(error):
    err = True
    msg = "Bad request made"
    appData = {} # empty object
    return make_response(jsonify(error=err, data=appData, message=msg), 400)

@app.errorhandler(401)
def unauthorized_access(error):
    err = True
    msg = "Unauthorized Access - Invalid credentials"
    appData = {} # empty object
    return make_response(jsonify(error=err, data=appData, message=msg), 401)

@app.errorhandler(405)
def method_not_allowed(error):
    err = True
    msg = "The method is not allowed for the requested URL"
    appData = {} # empty object
    return make_response(jsonify(error=err, data=appData, message=msg), 405)

@app.errorhandler(500)
def internal_server_error(error):
    err = True
    msg = "Connection error"
    appData = {} # empty object
    return make_response(jsonify(error=err, data=appData, message=msg), 500)
    
if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0",port="8080")
