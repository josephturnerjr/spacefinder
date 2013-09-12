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
def submit():
    return render_template('submit.html')


@views.route('/submit', methods=['POST'])
def submit_listing():
    address = request.form.get('address')
    lat = request.form.get('lat')
    lon = request.form.get('lon')
    space_type = request.form.get('space_type')
    price = request.form.get('price')
    description = request.form.get('description')
    if not all([address, lat, lon, space_type, price, description]):
        abort(500)
    try:
        price = float(price)
    except ValueError:
        abort(500)
    # TODO check space type
    listing = Listing(address, lat, lon, space_type, price, description)
    db.session.add(listing)
    db.session.commit()
    return ""


@views.route('/admin')
def admin():
    listings = Listing.query.all()
    unpublished = filter(lambda x: not x.published, listings)
    published = filter(lambda x: x.published, listings)
    return render_template('admin.html', published=published, unpublished=unpublished)
