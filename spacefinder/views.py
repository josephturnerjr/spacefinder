from spacefinder import app
from flask import (Blueprint, request, redirect,
                   render_template, session, abort)
from models import Listing, Account, db
from password import check_pw


views = Blueprint('spacefinder_views', __name__)


@app.template_filter('currency')
def format_currency(value):
    return "${:,.0f}".format(value)


@views.route('/')
def index():
    listings = Listing.query.filter_by(published=True).all()
    return render_template('index.html', listings=listings)

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
    print request.form, address, lat, lon
    if not all([address, lat, lon]):
        return redirect('/submit')
    return render_template('submit2.html', address=address, lat=lat, lon=lon)

@views.route('/submit/step2', methods=['POST'])
def submit_step2():
    address = request.form.get('address')
    lat = request.form.get('latitude')
    lon = request.form.get('longitude')
    print address, lat, lon
    if not all([address, lat, lon]):
        return redirect('/submit')
    space_type = request.form.get('space_type')
    price = request.form.get('price')
    description = request.form.get('description')
    if not all([space_type, price, description]):
        return render_template('submit2.html', address=address, lat=lat, lon=lon, price=price, space_type=space_type, description=description, error="All fields must be filled in")
    try:
        price = float(price)
    except ValueError:
        return render_template('submit2.html', address=address, lat=lat, lon=lon, price=price, space_type=space_type, description=description, error="Price must be a number")
    # TODO check space type
    create_listing(address, lat, lon, space_type, price, description)
    return render_template("thankyou.html")

def create_listing(address, lat, lon, space_type, price, description):
    listing = Listing(address, lat, lon, space_type, price, description)
    db.session.add(listing)
    db.session.commit()


@views.route('/admin')
def admin():
    listings = Listing.query.all()
    unpublished = filter(lambda x: not x.published, listings)
    published = filter(lambda x: x.published, listings)
    return render_template('admin.html', published=published, unpublished=unpublished)


@views.route('/admin/listing/<int:listing_id>/publish')
def publish(listing_id):
    listing = Listing.query.get(listing_id)
    if listing:
        listing.published = True
        db.session.add(listing)
        db.session.commit()
    return redirect('/admin')

@views.route('/admin/listing/<int:listing_id>/unpublish')
def unpublish(listing_id):
    listing = Listing.query.get(listing_id)
    if listing:
        listing.published = False
        db.session.add(listing)
        db.session.commit()
    return redirect('/admin')

@views.route('/admin/listing/<int:listing_id>/delete')
def delete_listing(listing_id):
    listing = Listing.query.get(listing_id)
    if listing:
        db.session.delete(listing)
        db.session.commit()
    return redirect('/admin')
