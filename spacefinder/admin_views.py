from spacefinder import app
from flask import (Blueprint,
                   request,
                   redirect,
                   render_template,
                   session,
                   abort)
from models import (Listing,
                    Account,
                    ListingType,
                    db,
                    get_space_type)
from functools import wraps


views = Blueprint('spacefinder_admin_views', __name__)


def requires_login(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        session_id = session.get("session_id")
        if not session_id:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated


# Admin functions
@views.route('/')
@requires_login
def admin():
    listings = Listing.query.all()
    accounts = Account.query.all()
    listing_types = ListingType.query.all()
    unpublished = filter(lambda x: not x.published, listings)
    published = filter(lambda x: x.published, listings)
    return render_template('admin.html',
                           published=published,
                           unpublished=unpublished,
                           accounts=accounts,
                           types=listing_types)


@views.route('/listing/<int:listing_id>/publish')
@requires_login
def publish(listing_id):
    listing = Listing.query.get(listing_id)
    if listing:
        listing.published = True
        db.session.add(listing)
        db.session.commit()
    return redirect('/')


@views.route('/listing/<int:listing_id>/unpublish')
@requires_login
def unpublish(listing_id):
    listing = Listing.query.get(listing_id)
    if listing:
        listing.published = False
        db.session.add(listing)
        db.session.commit()
    return redirect('/')


@views.route('/listing/<int:listing_id>/delete')
@requires_login
def delete_listing(listing_id):
    listing = Listing.query.get(listing_id)
    if listing:
        db.session.delete(listing)
        db.session.commit()
    return redirect('/')


@views.route('/listing/<int:listing_id>/edit')
@requires_login
def edit_listing(listing_id):
    listing = Listing.query.get(listing_id)
    if listing:
        listing_types = ListingType.query.all()
        return render_template('edit-listing.html',
                               listing=listing, address=listing.address,
                               lat=listing.latitude, lon=listing.longitude,
                               name=listing.name, price=listing.price,
                               space_type=listing.space_type,
                               types=listing_types,
                               description=listing.description)
    return redirect('/')


@views.route('/listing/<int:listing_id>/edit', methods=['POST'])
@requires_login
def edit_step_2(listing_id):
    listing = Listing.query.get(listing_id)
    if not listing:
        return redirect('/')
    address = request.form.get('address')
    lat = request.form.get('latitude')
    lon = request.form.get('longitude')
    if not all([address, lat, lon]):
        return redirect('/submit')
    space_type = get_space_type(request.form.get('space_type'))
    if not space_type:
        return redirect('/submit')
    price = request.form.get('price')
    description = request.form.get('description')
    name = request.form.get('name')
    listing_types = ListingType.query.all()
    if not all([space_type, price, name]):
        return render_template('edit-listing.html',
                               listing=listing, address=address, lat=lat,
                               lon=lon, name=name, price=price,
                               space_type=space_type, description=description,
                               types=listing_types,
                               error="All required fields must be filled in")
    try:
        price = float(price)
    except ValueError:
        return render_template('edit-listing.html',
                               listing=listing, address=address, lat=lat,
                               lon=lon, name=name, price=price,
                               space_type=space_type, description=description,
                               types=listing_types,
                               error="Price must be a number")
    listing.name = name
    listing.space_type = space_type
    listing.price = price
    listing.description = description
    db.session.add(listing)
    db.session.commit()
    return redirect('/')


@views.route('/account/<int:account_id>/delete')
@requires_login
def delete_account(account_id):
    account = Account.query.get(account_id)
    if account:
        db.session.delete(account)
        db.session.commit()
    return redirect('/')


@views.route('/account/create', methods=['POST'])
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
    return redirect('/')


@views.route('/listing_type/<int:listing_type_id>/delete')
@requires_login
def delete_listing_type(listing_type_id):
    listing_type = ListingType.query.get(listing_type_id)
    if listing_type:
        db.session.delete(listing_type)
        db.session.commit()
    return redirect('/')


@views.route('/listing_type/create', methods=['POST'])
@requires_login
def create_listing_type():
    name = request.form.get('name')
    if not name:
        abort(500)
    listing_type = ListingType(name)
    db.session.add(listing_type)
    db.session.commit()
    return redirect('/')
