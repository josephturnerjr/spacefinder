from spacefinder import app
from flask import (Blueprint, request, redirect,
                   render_template, session, abort)
from models import Listing, Account, ListingType, db
from password import check_pw
import sqlalchemy
import json
from functools import wraps


views = Blueprint('spacefinder_views', __name__)


def requires_login(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        session_id = session.get("session_id")
        if not session_id:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated


@app.template_filter('currency')
def format_currency(value):
    return "${:,.0f}".format(value)


@views.route('/')
def index():
    listings = Listing.query.filter_by(published=True).all()
    locations = [[float(l.latitude), float(l.longitude), l.name] for l in listings]
    return render_template('index.html', listings=listings, locations = locations)


@views.route('/login')
def login():
    return render_template('login.html')


@views.route('/login', methods=['POST'])
def log_user_in():
    username = request.form.get('username')
    password = request.form.get('password')
    if not all([username, password]):
        abort(500)
    # case-insensitive usernames
    username = username.lower()
    user = Account.query.filter_by(username=username).first()
    if user:
        if check_pw(password, user.pw_hash):
            # Valid password
            session.permanent = True
            session['session_id'] = user.id
            session['name'] = user.username
            return ""
    # Don't leak information
    abort(401)


@views.route('/logout', methods=['POST'])
def log_user_out():
    session.pop("session_id", None)
    session.pop("name", None)
    return redirect('/')


@views.route('/submit')
@views.route('/submit/step2')
def submit():
    return render_template('submit.html')


@views.route('/submit', methods=['POST'])
def submit_step1():
    address = request.form.get('formatted-address')
    lat = request.form.get('latitude')
    lon = request.form.get('longitude')
    if not all([address, lat, lon]):
        return redirect('/submit')
    listing_types = ListingType.query.all()
    return render_template('submit2.html', types=listing_types, address=address, lat=lat, lon=lon)


@views.route('/submit/step2', methods=['POST'])
def submit_step2():
    address = request.form.get('address')
    lat = request.form.get('latitude')
    lon = request.form.get('longitude')
    if not all([address, lat, lon]):
        return redirect('/submit')
    space_type = request.form.get('space_type')
    try:
        # Check that we've received a valid type id
        # Otherwise bogus form submission
        space_type = int(space_type)
        t = ListingType.query.get(space_type)
        if not t:
            return redirect('/submit')
    except TypeError:
        return redirect('/submit')
    price = request.form.get('price')
    description = request.form.get('description')
    name = request.form.get('name')
    listing_types = ListingType.query.all()
    if not all([space_type, price, name]):
        return render_template('submit2.html',
                                types=listing_types,
                                address=address, lat=lat, lon=lon,
                                name=name, price=price, space_type=space_type,
                                description=description,
                                error="All required fields must be filled in")
    try:
        price = float(price)
    except ValueError:
        return render_template('submit2.html',
                                types=listing_types,
                                address=address,
                                lat=lat, lon=lon, name=name, price=price,
                                space_type=space_type,
                                description=description, error="Price must be a number")
    try:
        create_listing(address, lat, lon, name, space_type, price, description)
    except sqlalchemy.exc.IntegrityError:
        return render_template('submit2.html',
                                types=listing_types,
                                address=address, lat=lat,
                                lon=lon, name=name, price=price,
                                space_type=space_type,
                                description=description,
                                error="Space type must be one of meeting or office")
    return render_template("thankyou.html")


def create_listing(address, lat, lon, name, space_type, price, description):
    listing = Listing(address, lat, lon, name, space_type, price, description)
    db.session.add(listing)
    db.session.commit()


@views.route('/listing/<int:listing_id>')
def listing(listing_id):
    listing = Listing.query.get_or_404(listing_id)
    if not (listing.published or session.get('session_id')):
        print "abortin"
        abort(404)
    return render_template('listing.html', listing=listing)


@views.route('/admin')
@requires_login
def admin():
    listings = Listing.query.all()
    accounts = Account.query.all()
    listing_types = ListingType.query.all()
    unpublished = filter(lambda x: not x.published, listings)
    published = filter(lambda x: x.published, listings)
    return render_template('admin.html', published=published, unpublished=unpublished, accounts=accounts, types=listing_types)


@views.route('/admin/listing/<int:listing_id>/publish')
@requires_login
def publish(listing_id):
    listing = Listing.query.get(listing_id)
    if listing:
        listing.published = True
        db.session.add(listing)
        db.session.commit()
    return redirect('/admin')


@views.route('/admin/listing/<int:listing_id>/unpublish')
@requires_login
def unpublish(listing_id):
    listing = Listing.query.get(listing_id)
    if listing:
        listing.published = False
        db.session.add(listing)
        db.session.commit()
    return redirect('/admin')


@views.route('/admin/listing/<int:listing_id>/delete')
@requires_login
def delete_listing(listing_id):
    listing = Listing.query.get(listing_id)
    if listing:
        db.session.delete(listing)
        db.session.commit()
    return redirect('/admin')


@views.route('/admin/listing/<int:listing_id>/edit')
@requires_login
def edit_listing(listing_id):
    listing = Listing.query.get(listing_id)
    if listing:
        return render_template('edit-listing.html',
                                listing=listing, address=listing.address,
                                lat=listing.latitude, lon=listing.longitude,
                                name=listing.name, price=listing.price,
                                space_type=listing.space_type,
                                description=listing.description)
    return redirect('/admin')


@views.route('/admin/listing/<int:listing_id>/edit', methods=['POST'])
@requires_login
def edit_step_2(listing_id):
    listing = Listing.query.get(listing_id)
    if not listing:
        return redirect('/admin')
    address = request.form.get('address')
    lat = request.form.get('latitude')
    lon = request.form.get('longitude')
    if not all([address, lat, lon]):
        return redirect('/submit')
    space_type = request.form.get('space_type')
    price = request.form.get('price')
    description = request.form.get('description')
    name = request.form.get('name')
    if not all([space_type, price, description, name]):
        return render_template('edit-listing.html',
                                listing=listing, address=address, lat=lat,
                                lon=lon, name=name, price=price,
                                space_type=space_type, description=description,
                                error="All required fields must be filled in")
    try:
        price = float(price)
    except ValueError:
        return render_template('edit-listing.html',
                                listing=listing, address=address, lat=lat,
                                lon=lon, name=name, price=price,
                                space_type=space_type, description=description,
                                error="Price must be a number")
    try:
        listing.name = name
        listing.space_type = space_type
        listing.price = price
        listing.description = description
        db.session.add(listing)
        db.session.commit()
    except sqlalchemy.exc.IntegrityError:
        return render_template('edit-listing.html',
                                listing=listing,
                                address=address, lat=lat, lon=lon, name=name,
                                price=price, space_type=space_type,
                                description=description,
                                error="Space type must be one of meeting or office")
    return redirect('/admin')


@views.route('/admin/account/<int:account_id>/delete')
@requires_login
def delete_account(account_id):
    account = Account.query.get(account_id)
    if account:
        db.session.delete(account)
        db.session.commit()
    return redirect('/admin')

@views.route('/admin/account/create', methods=['POST'])
@requires_login
def create_account():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    if not all([username, email, password]):
        abort(500)
    account = Account(username, email, password)
    db.session.add(account)
    db.session.commit()
    return redirect('/admin')


@views.route('/admin/listing_type/<int:listing_type_id>/delete')
@requires_login
def delete_listing_type(listing_type_id):
    listing_type = ListingType.query.get(listing_type_id)
    if listing_type:
        db.session.delete(listing_type)
        db.session.commit()
    return redirect('/admin')

@views.route('/admin/listing_type/create', methods=['POST'])
@requires_login
def create_listing_type():
    name = request.form.get('name')
    if not name:
        abort(500)
    listing_type = ListingType(name)
    db.session.add(listing_type)
    db.session.commit()
    return redirect('/admin')
