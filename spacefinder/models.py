from flask_sqlalchemy import SQLAlchemy
from spacefinder import app
import datetime
import md5
from password import hash_pw
from uuid import uuid4
from sqlalchemy.ext.hybrid import hybrid_property
from PIL import Image
import os

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
    ada_accessible = db.Column(db.Boolean(), default=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    contact_phone = db.Column(db.String(16), nullable=False)
    contact_email = db.Column(db.String(100))
    address = db.Column(db.String(240), nullable=False)
    latitude = db.Column(db.String(16), nullable=False)
    longitude = db.Column(db.String(16), nullable=False)
    space_type_id = db.Column(db.Integer, db.ForeignKey('listing_types.id'), nullable=False)
    space_type = db.relationship("ListingType")
    price = db.Column(db.Float(), nullable=False)
    rate_type_id = db.Column(db.Integer, db.ForeignKey('rate_types.id'), nullable=False)
    rate_type = db.relationship("RateType")
    description = db.Column(db.Text(), nullable=False)
    created = db.Column(db.DateTime, nullable=False)
    expires = db.Column(db.DateTime, nullable=False)

    def __init__(self,
                 address,
                 lat,
                 lon,
                 name,
                 space_type,
                 rate_type,
                 price,
                 description,
                 contact_phone,
                 contact_email=None,
                 ada_accessible=True,
                 expires_in_days=90):
        self.address = address
        self.latitude = lat
        self.longitude = lon
        self.name = name
        self.contact_phone = contact_phone
        self.contact_email = contact_email
        self.space_type_id = space_type.id
        self.rate_type_id = rate_type.id
        self.price = price
        self.ada_accessible = ada_accessible
        self.description = description
        self.created = datetime.datetime.today()
        self.expires = datetime.datetime.utcnow() + datetime.timedelta(days=expires_in_days)

    @hybrid_property
    def expired(self):
        return self.expires <= datetime.datetime.utcnow()


class ListingType(db.Model):
    __tablename__ = "listing_types"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    def __init__(self, name):
        self.name = name


class RateType(db.Model):
    __tablename__ = "rate_types"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<RateType: %s>" % self.name

"""
It's unclear whether this is necessary or not

class ExpirationTimeframe(db.Model):
    __tablename__ = "expiration_timeframes"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    days = db.Column(db.Integer, nullable=False)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<ExpirationTimeframe: %s (%s days)>" % (self.name, self.days)
"""


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


class SubmissionPhoto(db.Model):
    __tablename__ = "submission_photos"
    ALLOWED_EXTENSIONS = ('jpg', 'gif', 'png', 'jpeg')
    THUMB_SIZE = (256, 256)
    id = db.Column(db.Integer, primary_key=True)
    created_on = db.Column(db.DateTime())
    filename = db.Column(db.String(256))
    thumbnail = db.Column(db.String(256))
    listing_id = db.Column(db.Integer, db.ForeignKey('listings.id'))
    listing = db.relationship('Listing', backref=db.backref('photos'))

    def __init__(self, f):
        self.created_on = datetime.datetime.now()
        img = Image.open(f)
        # Convert image to jpg for space
        filename = "%s.jpg" % uuid4()
        filepath = os.path.join(app.config["IMG_STORAGE"], filename)
        img.save(filepath)
        # Save a thumbnail for intermediary display
        img.thumbnail(self.THUMB_SIZE, Image.ANTIALIAS)
        thumb_name = "%s.jpg" % uuid4()
        thumb_path = os.path.join(app.config["IMG_STORAGE"], thumb_name)
        img.save(thumb_path)
        # Record the file paths
        self.filename = filename
        self.thumbnail = thumb_name


class Benefactor(db.Model):
    __tablename__ = "benefactors"
    THUMB_SIZE = (256, 256)
    id = db.Column(db.Integer, primary_key=True)
    created_on = db.Column(db.DateTime())
    logo_filename = db.Column(db.String(256))
    thumbnail = db.Column(db.String(256))
    name = db.Column(db.String(256))
    website = db.Column(db.String(1024))

    def __init__(self, name, img_f, website=None):
        self.name = name
        self.website = website
        self.created_on = datetime.datetime.now()
        img = Image.open(img_f)
        # Convert image to jpg for space
        filename = "%s.jpg" % uuid4()
        filepath = os.path.join(app.config["IMG_STORAGE"], filename)
        img.save(filepath)
        # Save a thumbnail for intermediary display
        img.thumbnail(self.THUMB_SIZE, Image.ANTIALIAS)
        thumb_name = "%s.jpg" % uuid4()
        thumb_path = os.path.join(app.config["IMG_STORAGE"], thumb_name)
        img.save(thumb_path)
        # Record the file paths
        self.logo_filename = filename
        self.thumbnail = thumb_name


def get_space_type(type_id):
    try:
        # Check that we've received a valid type id
        # Otherwise bogus form submission
        space_type = int(type_id)
        t = ListingType.query.get(space_type)
        return t
    except TypeError:
        return None


def get_rate_type(type_id):
    try:
        # Check that we've received a valid type id
        # Otherwise bogus form submission
        rate_type = int(type_id)
        t = RateType.query.get(rate_type)
        return t
    except TypeError:
        return None
