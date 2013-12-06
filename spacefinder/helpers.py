from models import Listing, get_space_type, get_rate_type, db
import datetime


class FormError(Exception):
    pass


class FieldError(Exception):
    pass


def edit_listing(listing, request):
    if not listing:
        raise FormError()
    address = request.form.get('address')
    lat = request.form.get('latitude')
    lon = request.form.get('longitude')
    if not all([address, lat, lon]):
        raise FormError()
    space_type = get_space_type(request.form.get('space_type'))
    if not space_type:
        raise FormError()
    rate_type = get_rate_type(request.form.get('rate_type'))
    if not rate_type:
        raise FormError()
    price = request.form.get('price')
    description = request.form.get('description')
    name = request.form.get('name')
    if not all([space_type, price, name]):
        raise FieldError("All required fields must be filled in")
    try:
        price = float(price)
    except ValueError:
        raise FieldError("Price must be a number")
    listing.name = name
    listing.space_type = space_type
    listing.rate_type = rate_type
    listing.price = price
    listing.description = description
    db.session.add(listing)
    db.session.commit()


def expire_listings():
    Listing.query.filter(Listing.expires <= datetime.datetime.utcnow()).update({'expired': True})
    db.session.commit()


def renew_listing(listing, expires_in_days=90):
    listing.expired = False
    listing.expires = datetime.datetime.utcnow() + datetime.timedelta(days=expires_in_days)
    db.session.add(listing)
    db.session.commit()
