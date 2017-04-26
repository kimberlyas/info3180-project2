from . import db
from werkzeug.security import generate_password_hash, check_password_hash

# Relationship table ( one user - many wishes)
users_wishes = db.Table('users_wishes',
        db.Column('user_id', db.Integer, db.ForeignKey('user_profile.id')), 
        db.Column('wish_id', db.Integer, db.ForeignKey('wish.item_id')))
    
# User
class UserProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    name = db.Column(db.String(80))
    age = db.Column(db.Integer)
    gender = db.Column(db.String(1))
    image = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    created_on = db.Column(db.String(80))
    wishes = db.relationship('Wish', secondary=users_wishes, backref=db.backref('userprofiles', lazy='dynamic'))
    
    def __init__(self, userid, name, age, sex, imageFile, email, password, creation_date):
        self.id = userid
        self.name = name
        self.age = age
        self.gender = sex
        self.image = imageFile
        self.email = email
        self.password = generate_password_hash(password)
        self.created_on = creation_date
        
    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return unicode(self.id)  # python 2 support
        except NameError:
            return str(self.id)  # python 3 support

    def __repr__(self):
        return '<User %r>' % (self.name)


# Wishlist Item
class Wish(db.Model):
    item_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.Text)
    url = db.Column(db.String(255))
    thumbnail = db.Column(db.String(255))

    def __init__(self, title, description, address, imageUrl):
        self.title = title
        self.description = description
        self.url = address
        self.thumbnail = imageUrl
    
    def get_id(self):
        try:
            return unicode(self.item_id)  # python 2 support
        except NameError:
            return str(self.item_id)  # python 3 support
    
    def __repr__(self):
        return '<Item %r>' % (self.title)


    