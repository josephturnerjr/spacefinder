from spacefinder import app
from flask import (Blueprint, request, redirect,
                   render_template, session, abort, send_from_directory, url_for)
from models import (Listing, Account, ListingType, Submitter, RateType,
                    SubmissionToken, SubmissionPhoto, db, get_space_type, get_rate_type)
from password import check_pw
import sf_email
import helpers
import datetime


views = Blueprint('spacefinder_views', __name__)


@app.template_filter('currency')
def format_currency(value):
    return "${:,.0f}".format(value)


@app.template_filter('safe_email')
def format_safe_email(email):
    return email.replace("@", " (at) ").replace(".", " (dot) ")


@app.template_filter('phone')
def format_phone_number(phone):
    if len(phone) == 7:
        return "%s - %s" % (phone[:3], phone[3:])
    elif len(phone) == 10:
        return "(%s) %s - %s" % (phone[:3], phone[3:6], phone[6:])


# Browsing (public) functions
@views.route('/')
def index():
    listings = Listing.query.filter_by(expired=False).filter_by(published=True).all()
    locations = [[float(l.latitude), float(l.longitude), l.name] for l in listings]
    return render_template('index.html',
                           listings=listings,
                           locations=locations)


@app.route('/images/<filename>')
def submission_image(filename):
    attach = False
    if request.args.get('dl'):
        attach = True
    return send_from_directory(app.config['IMG_STORAGE'],
                               filename,
                               as_attachment=attach)


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
    fields = ['orgaddr1', 'orgaddr2', 'orgcity', 'orgstate', 'orgzip']
    addr_parts = [request.form.get(x, '') for x in fields]
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


@views.route('/submission/<token>/photos')
def submission_photos(token):
    # Look up token
    token = SubmissionToken.query.filter(SubmissionToken.key == token).first()
    if not token:
        return redirect('/submit')
    # See if token has submitted
    if not token.listing:
        return redirect('/submission/%s' % token.key)
    return render_template('photos-submission.html',
                           token=token,
                           listing=token.listing)


@views.route('/submission/<token_>/photos', methods=['POST'])
def submit_photo(token_):
    # Look up token
    token = SubmissionToken.query.filter(SubmissionToken.key == token_).first()
    if not token:
        return redirect('/submit')
    # See if token has submitted
    if not token.listing:
        return redirect('/submission/%s' % token.key)
    if not request.files.get('photo'):
        return redirect(url_for('.submission_photos', token=token_))
    token.listing.photos.append(SubmissionPhoto(request.files['photo']))
    db.session.add(token)
    db.session.commit()
    return redirect(url_for('.submission_photos', token=token_))


@views.route("/submission/<token>/photos/<int:photo_id>", methods=["DELETE"])
def delete_image(token, photo_id):
    token = SubmissionToken.query.filter(SubmissionToken.key == token).first()
    if not token:
        return redirect('/submit')
    # See if token has submitted
    if not token.listing:
        return redirect('/submission/%s' % token.key)
    photo = SubmissionPhoto.query.get_or_404(photo_id)
    if not photo.listing == token.listing:
        return redirect('/submit')
    db.session.delete(photo)
    db.session.commit()
    return ""



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
                           rate_types=rate_types,
                           token=token,
                           listing={
                               "address": address,
                               "latitude": lat,
                               "longitude": lon,
                               "ada_accessible": True,
                           })


@views.route('/submission/<token>/submit/step2', methods=['POST'])
def submit_step2(token):
    # Look up token
    token = SubmissionToken.query.filter(SubmissionToken.key == token).first()
    # Check for a real token and that they havent already submitted
    print request.form
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
    expires_in_days = request.form.get('expires_in_days')
    ada_accessible = request.form.get('ada_accessible')
    if ada_accessible == "no":
        ada_accessible = False
    else:
        ada_accessible = True
    contact_phone = request.form.get('contact_phone')
    contact_email = request.form.get('contact_email')
    listing={
        "address": address,
        "latitude": lat,
        "longitude": lon,
        "name": name,
        "price": price,
        "space_type": space_type,
        "description": description,
        "contact_email": contact_email,
        "contact_phone": contact_phone,
        "ada_accessible": ada_accessible
    }
    if not all([space_type, price, name, description, contact_phone]):
        return render_template('submit2.html',
                               types=listing_types,
                               rate_types=rate_types,
                               token=token,
                               listing=listing,
                               error="All required fields must be filled in")
    try:
        try:
            if price.startswith('$'):
                price = price[1:]
            price = float(price)
        except:
            raise Exception("Price must be a number")
        try:
            expires_in_days = int(expires_in_days)
        except:
            raise Exception("Expiration must be a number of days")
    except Exception, e:
        return render_template('submit2.html',
                               types=listing_types,
                               rate_types=rate_types,
                               token=token,
                               listing=listing,
                               error=str(e))
    listing = Listing(address=address,
                      lat=lat,
                      lon=lon,
                      name=name,
                      space_type=space_type,
                      rate_type=rate_type,
                      price=price,
                      description=description,
                      ada_accessible=ada_accessible,
                      contact_email=contact_email,
                      contact_phone=contact_phone,
                      expires_in_days=expires_in_days)
    db.session.add(listing)
    db.session.commit()
    token.listing = listing
    db.session.add(token)
    db.session.commit()
    return redirect("/submission/%s" % token.key)


    return listing
