from flask_sqlalchemy import SQLAlchemy
from spacefinder import app
import datetime
import md5
from password import hash_pw

db = SQLAlchemy(app)


class Account(db.Model):
    """
        The Account model represents a single username/password combination
        and the associated metadata.
        Each Account is associated with an organization.
    """
    __tablename__ = "accounts"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    pw_hash = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    signup_on = db.Column(db.DateTime, nullable=False)
    name = db.Column(db.String(120))

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.set_pw(password)
        self.signup_on = datetime.datetime.today()

    def set_pw(self, password):
        self.pw_hash = hash_pw(password)

    @property
    def email_hash(self):
        return md5.new(self.email.strip().lower()).hexdigest()

    def __repr__(self):
        return '<User %r>' % self.username


class Listing(db.Model):
    __tablename__ = "listings"
    id = db.Column(db.Integer, primary_key=True)
    published = db.Column(db.Boolean(), default=False, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(240), nullable=False)
    latitude = db.Column(db.String(16), nullable=False)
    longitude = db.Column(db.String(16), nullable=False) 
    space_type = db.Column(db.Enum('office', 'meeting'), nullable=False)
    price = db.Column(db.Float(), nullable=False)
    description = db.Column(db.Text(), nullable=False)
    created = db.Column(db.DateTime, nullable=False)

    def __init__(self, address, lat, lon, name, space_type, price, description):
        self.address = address
        self.latitude = lat
        self.longitude = lon
        self.name = name
        self.space_type = space_type
        self.price = price
        self.description = description
        self.created = datetime.datetime.today()
