from spacefinder import app
from flask import (Blueprint,
                   request,
                   redirect,
                   url_for,
                   render_template,
                   session,
                   abort)
from models import (Listing,
                    Benefactor,
                    Account,
                    RateType,
                    Submitter,
                    ListingType,
                    db)
from functools import wraps
import helpers


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
    rate_types = RateType.query.all()
    submitters = Submitter.query.all()
    unpublished = filter(lambda x: not x.published and not x.expired, listings)
    published = filter(lambda x: x.published and not x.expired, listings)
    expired = filter(lambda x: x.expired, listings)
    benefactors = Benefactor.query.all()
    return render_template('admin.html',
                           published=published,
                           unpublished=unpublished,
                           expired=expired,
                           accounts=accounts,
                           rate_types=rate_types,
                           submitters=submitters,
                           benefactors=benefactors,
                           types=listing_types)


@views.route('/listing/<int:listing_id>/renew')
@requires_login
def renew(listing_id):
    listing = Listing.query.get(listing_id)
    if listing:
        helpers.renew_listing(listing)
    return redirect(url_for('.admin'))


@views.route('/listing/<int:listing_id>/publish')
@requires_login
def publish(listing_id):
    listing = Listing.query.get(listing_id)
    if listing:
        listing.published = True
        db.session.add(listing)
        db.session.commit()
    return redirect(url_for('.admin'))


@views.route('/listing/<int:listing_id>/unpublish')
@requires_login
def unpublish(listing_id):
    listing = Listing.query.get(listing_id)
    if listing:
        listing.published = False
        db.session.add(listing)
        db.session.commit()
    return redirect(url_for('.admin'))


@views.route('/listing/<int:listing_id>/delete')
@requires_login
def delete_listing(listing_id):
    listing = Listing.query.get(listing_id)
    if listing:
        db.session.delete(listing)
        db.session.commit()
    return redirect(url_for('.admin'))


@views.route('/listing/<int:listing_id>/edit')
@requires_login
def edit_listing(listing_id):
    listing = Listing.query.get(listing_id)
    if listing:
        listing_types = ListingType.query.all()
        rate_types = RateType.query.all()
        return render_template('edit-listing.html',
                               listing=listing, address=listing.address,
                               lat=listing.latitude, lon=listing.longitude,
                               name=listing.name, price=listing.price,
                               space_type=listing.space_type,
                               types=listing_types,
                               rate_types=rate_types,
                               description=listing.description)
    return redirect(url_for('.admin'))


@views.route('/listing/<int:listing_id>/edit', methods=['POST'])
@requires_login
def edit_step_2(listing_id):
    listing = Listing.query.get(listing_id)
    listing_types = ListingType.query.all()
    rate_types = RateType.query.all()
    try:
        helpers.edit_listing(listing, request)
    except helpers.FieldError, e:
        return render_template('edit-listing.html',
                               listing=listing,
                               rate_types=rate_types,
                               types=listing_types,
                               error=str(e))
    except helpers.FormError, e:
        return redirect('/submit')
    return redirect(url_for('.admin'))


@views.route('/account/<int:account_id>/delete')
@requires_login
def delete_account(account_id):
    account = Account.query.get(account_id)
    if account:
        db.session.delete(account)
        db.session.commit()
    return redirect(url_for('.admin'))


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
    return redirect(url_for('.admin'))


@views.route('/listing_type/<int:listing_type_id>/delete')
@requires_login
def delete_listing_type(listing_type_id):
    return delete_named_item(ListingType, listing_type_id)


@views.route('/listing_type/create', methods=['POST'])
@requires_login
def create_listing_type():
    return create_named_item(ListingType)


@views.route('/rate_type/<int:type_id>/delete')
@requires_login
def delete_rate_type(type_id):
    return delete_named_item(RateType, type_id)


@views.route('/rate_type/create', methods=['POST'])
@requires_login
def create_rate_type():
    return create_named_item(RateType)


def delete_named_item(item_class, item_id, redirect_url=None):
    redirect_url = redirect_url or url_for('.admin')
    item = item_class.query.get(item_id)
    if item:
        db.session.delete(item)
        db.session.commit()
    return redirect(redirect_url)


def create_named_item(item_class, redirect_url=None):
    redirect_url = redirect_url or url_for('.admin')
    name = request.form.get('name')
    if not name:
        abort(500)
    item = item_class(name)
    db.session.add(item)
    db.session.commit()
    return redirect(redirect_url)


@views.route('/benefactors', methods=['POST'])
@requires_login
def create_benefactor():
    redirect_url = url_for('.admin')
    name = request.form.get('name')
    website = request.form.get('website')
    logo = request.files.get('logo')
    if not name or not logo:
        abort(500)
    benefactor = Benefactor(name=name, website=website, img_f=logo)
    db.session.add(benefactor)
    db.session.commit()
    return redirect(redirect_url)


@views.route('/benefactors/<int:id_>/delete')
@requires_login
def delete_benefactor(id_):
    return delete_named_item(Benefactor, id_)
