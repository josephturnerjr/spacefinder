from flask_sqlalchemy import SQLAlchemy
from spacefinder import app
import datetime
import md5
from password import hash_pw
from uuid import uuid4

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


class Submitter(db.Model):
    __tablename__ = "submitters"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    title = db.Column(db.String(24), nullable=False)
    organization_name = db.Column(db.String(100), nullable=False)
    organization_address = db.Column(db.String(500), nullable=False)
    organization_type = db.Column(db.Enum('nonprofit', 'for-profit'), nullable=False)
    mdnonprofit_member = db.Column(db.Boolean(), nullable=False)

    def __init__(self, name, email, phone, title, orgname, orgaddr, orgtype, member):
        self.name = name
        self.email = email
        self.phone = phone
        self.title = title
        self.organization_name = orgname
        self.organization_address = orgaddr
        self.organization_type = orgtype
        self.mdnonprofit_member = member
        self.token = SubmissionToken(email)


class Listing(db.Model):
    __tablename__ = "listings"
    id = db.Column(db.Integer, primary_key=True)
    published = db.Column(db.Boolean(), default=False, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(240), nullable=False)
    latitude = db.Column(db.String(16), nullable=False)
    longitude = db.Column(db.String(16), nullable=False)
    space_type_id = db.Column(db.Integer, db.ForeignKey('listing_types.id'), nullable=False)
    space_type = db.relationship("ListingType")
    price = db.Column(db.Float(), nullable=False)
    description = db.Column(db.Text(), nullable=False)
    created = db.Column(db.DateTime, nullable=False)

    def __init__(self, address, lat, lon, name, space_type, price, description):
        self.address = address
        self.latitude = lat
        self.longitude = lon
        self.name = name
        self.space_type_id = space_type.id
        self.price = price
        self.description = description
        self.created = datetime.datetime.today()


class ListingType(db.Model):
    __tablename__ = "listing_types"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    def __init__(self, name):
        self.name = name


class SubmissionToken(db.Model):
    __tablename__ = "submission_tokens"
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    listing_id = db.Column(db.Integer, db.ForeignKey('listings.id'))
    listing = db.relationship('Listing')
    submitter_id = db.Column(db.Integer, db.ForeignKey('submitters.id'), nullable=False)
    submitter = db.relationship('Submitter', backref=db.backref('token', uselist=False))

    def __init__(self, email):
        self.email = email
        self.key = str(uuid4())


def get_space_type(type_id):
    try:
        # Check that we've received a valid type id
        # Otherwise bogus form submission
        space_type = int(type_id)
        t = ListingType.query.get(space_type)
        return t
    except TypeError:
        return None
