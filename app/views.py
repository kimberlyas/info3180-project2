"""
Flask Documentation:     http://flask.pocoo.org/docs/
Jinja2 Documentation:    http://jinja.pocoo.org/2/documentation/
Werkzeug Documentation:  http://werkzeug.pocoo.org/documentation/
This file creates your application.
"""

from app import app, db, login_manager
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from forms import LoginForm
from models import UserProfile
from bs4 import BeautifulSoup
import requests
import urlparse


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

# GEORGIA
@app.route("/share/{userid}/wishlist")
def share_wishlist(): 
    """ Allows a user to share their wishlist with friends or family via email"""
    pass 

###
# API Routes
###
@app.route("/api/users/register", methods=["GET","POST"])
def signup():
    """ Accepts user information and saves it to the database """
    # Generate sign up form
    form = "SignupForm()"
    # Validate form
    # Get info
    # Save to DB
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
            # Get the email and password values from the form.
            email = form.email.data
            password = form.password.data
            
            # using your model, query database for a user based on the email
            # and password submitted
            # store the result of that query to a `user` variable so it can be
            # passed to the login_user() method.
            user = UserProfile.query.filter_by(email=email, password=password).first()
           
            if user is not None:
               
                # get user id, load into session
                login_user(user)

                # remember to flash a message to the user
                flash("You made it in!", 'success')
                
                # redirect to home page
                return redirect(url_for("home"))
            else:
                # Error message
                flash('Email or Password incorrect.', 'danger')
    # Load login page
    return render_template("login.html", form=form)

@app.route("/api/users/{userid}/wishlist", methods=["POST"])
@login_required
def add_item():
    """ Used for adding items to the wishlist """
    # Add form
    # Validate form
    # Get title
    # Get description
    # Get website address
    # Get thumbnail image
    # Save to DB
    return render_template('.html')

@app.route("/api/users/{userid}/wishlist/{itemid}", methods=["DELETE"])
@login_required
def delete_item():
    """ Deletes an item from a user's wishlist """
    return render_template('.html')

@app.route("/api/users/{userid}/wishlist", methods=["GET"])
def view_wishlist():
    """ Returns a user's wishlist """
    return render_template('wishlist.html')

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
    
    return jsonify(error=err, message=msg,thumbnails=urls)

###
# The functions below should be applicable to all Flask apps.
###

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
