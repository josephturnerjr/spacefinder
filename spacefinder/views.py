from spacefinder import app
from flask import (Blueprint, request, redirect,
                   render_template, session, abort)
from models import (Listing, Account, ListingType, Submitter, RateType,
                    SubmissionToken, db, get_space_type, get_rate_type)
from password import check_pw
import sf_email
import helpers
import datetime


views = Blueprint('spacefinder_views', __name__)


@app.template_filter('currency')
def format_currency(value):
    return "${:,.0f}".format(value)


# Browsing (public) functions
@views.route('/')
def index():
    listings = Listing.query.filter_by(expired=False).filter_by(published=True).all()
    locations = [[float(l.latitude), float(l.longitude), l.name] for l in listings]
    return render_template('index.html', listings=listings, locations = locations)


@views.route('/listing/<int:listing_id>')
def listing(listing_id):
    listing = Listing.query.get_or_404(listing_id)
    if not (listing.published or session.get('session_id')):
        abort(404)
    return render_template('listing.html', listing=listing)


# Auth functions
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


# Token creation functions
@views.route('/submit')
def submit():
    return render_template('get-token.html')


@views.route('/submit', methods=['POST'])
def create_token():
    email = request.form.get('email')
    name = request.form.get('name')
    phone = request.form.get('phone')
    title = request.form.get('title')
    orgname = request.form.get('orgname')
    orgtype = request.form.get('orgtype')
    member = request.form.get('member')
    addr_parts = [request.form.get(x, '') for x in ['orgaddr1', 'orgaddr2', 'orgcity', 'orgstate', 'orgzip']]
    if not all([email, name, orgname, orgtype]) or not any(addr_parts):
        return render_template('get-token.html', errors='All required fields must be filled in.')
    member = member == "yes"
    orgaddr = "\n".join(addr_parts)
    submitter = Submitter(name,
                          email,
                          phone,
                          title,
                          orgname,
                          orgaddr,
                          orgtype,
                          member)
    db.session.add(submitter)
    db.session.commit()
    # send the email
    sf_email.send_token(email, submitter.token.key)
    print "/submission/%s" % submitter.token.key
    return render_template('token-thanks.html')


# Token functions (post-signup)
@views.route('/submission/<token>')
def submission(token):
    # Look up token
    token = SubmissionToken.query.filter(SubmissionToken.key == token).first()
    if not token:
        return redirect('/submit')
    # See if token has submitted
    if token.listing:
        expires = token.listing.expires - datetime.datetime.utcnow()
        return render_template('post-submission.html',
                               token=token,
                               listing=token.listing,
                               expire_days=expires.days)
    else:
        return render_template('submit.html', token=token)


@views.route('/submission/<token>/view')
def view_submission(token):
    token = SubmissionToken.query.filter(SubmissionToken.key == token).first()
    if not token:
        return redirect('/submit')
    # See if token has submitted
    if not token.listing:
        return redirect('/submission/%s' % token.key)
    return render_template('listing.html', listing=token.listing)


@views.route('/submission/<token>/renew')
def renew_submission(token):
    token = SubmissionToken.query.filter(SubmissionToken.key == token).first()
    if not token:
        return redirect('/submit')
    # See if token has submitted
    if not token.listing:
        return redirect('/submission/%s' % token.key)
    if token.listing.expired:
        helpers.renew_listing(token.listing)
    return redirect('/submission/%s' % token.key)


@views.route('/submission/<token>/delete', methods=['POST'])
def delete_submission(token):
    token = SubmissionToken.query.filter(SubmissionToken.key == token).first()
    if not token:
        return redirect('/submit')
    # See if token has submitted
    if not token.listing:
        return redirect('/submission/%s' % token.key)
    # Remove the listing and the token
    db.session.delete(token.listing)
    db.session.delete(token)
    db.session.commit()
    return redirect('/')


@views.route('/submission/<token>/edit')
def edit_submission(token):
    # Look up token
    token = SubmissionToken.query.filter(SubmissionToken.key == token).first()
    if not token:
        return redirect('/submit')
    # See if token has submitted
    if not token.listing:
        return redirect('/submission/%s' % token.key)
    # If so, send to edit/delete admin page
    listing_types = ListingType.query.all()
    rate_types = RateType.query.all()
    return render_template('edit-submission.html',
                           token=token,
                           listing=token.listing,
                           rate_types=rate_types,
                           types=listing_types)


@views.route('/submission/<token>/edit', methods=['POST'])
def edit_submission_step2(token):
    token = SubmissionToken.query.filter(SubmissionToken.key == token).first()
    if not token:
        return redirect('/submit')
    # See if token has submitted
    if not token.listing:
        return redirect('/submission/%s' % token.key)
    listing_types = ListingType.query.all()
    rate_types = RateType.query.all()
    try:
        helpers.edit_listing(token.listing, request)
    except helpers.FieldError, e:
        return render_template('edit-submission.html',
                               listing=token.listing,
                               rate_types=rate_types,
                               types=listing_types,
                               error=str(e))
    except helpers.FormError, e:
        return redirect('/submit')
    # On successful edit, requeue the listing for curation
    token.listing.published = False
    db.session.add(token.listing)
    db.session.commit()
    return redirect('/submission/%s' % token.key)


@views.route('/submission/<token>/submit', methods=['POST'])
def submit_step1(token):
    # Look up token
    token = SubmissionToken.query.filter(SubmissionToken.key == token).first()
    if not token:
        return redirect('/submit')
    address = request.form.get('formatted-address')
    lat = request.form.get('latitude')
    lon = request.form.get('longitude')
    if not all([address, lat, lon]):
        return redirect('/submit')
    listing_types = ListingType.query.all()
    rate_types = RateType.query.all()
    return render_template('submit2.html',
                           types=listing_types,
                           address=address,
                           lat=lat,
                           lon=lon,
                           rate_types=rate_types,
                           token=token)


@views.route('/submission/<token>/submit/step2', methods=['POST'])
def submit_step2(token):
    # Look up token
    token = SubmissionToken.query.filter(SubmissionToken.key == token).first()
    # Check for a real token and that they havent already submitted
    if not token or token.listing:
        return redirect('/submit')
    address = request.form.get('address')
    lat = request.form.get('latitude')
    lon = request.form.get('longitude')
    if not all([address, lat, lon]):
        return redirect('/submit')
    space_type = get_space_type(request.form.get('space_type'))
    if not space_type:
        return redirect('/submit')
    rate_type = get_rate_type(request.form.get('rate_type'))
    if not rate_type:
        return redirect('/submit')
    price = request.form.get('price')
    description = request.form.get('description')
    name = request.form.get('name')
    listing_types = ListingType.query.all()
    rate_types = RateType.query.all()
    if not all([space_type, price, name, description]):
        return render_template('submit2.html',
                               types=listing_types,
                               address=address,
                               lat=lat,
                               lon=lon,
                               name=name,
                               price=price,
                               space_type=space_type,
                               description=description,
                               rate_types=rate_types,
                               token=token,
                               error="All required fields must be filled in")
    try:
        if price.startswith('$'):
            price = price[1:]
        price = float(price)
    except ValueError:
        return render_template('submit2.html',
                               types=listing_types,
                               address=address,
                               lat=lat,
                               lon=lon,
                               name=name,
                               price=price,
                               space_type=space_type,
                               token=token,
                               rate_types=rate_types,
                               description=description,
                               error="Price must be a number")
    listing = create_listing(address,
                             lat,
                             lon,
                             name,
                             space_type,
                             rate_type,
                             price,
                             description)
    token.listing = listing
    db.session.add(token)
    db.session.commit()
    return redirect("/submission/%s" % token.key)


#Helpers
def create_listing(address, lat, lon, name, space_type, rate_type, price, description):
    listing = Listing(address, lat, lon, name, space_type, rate_type, price, description)
    db.session.add(listing)
    db.session.commit()
    return listing
