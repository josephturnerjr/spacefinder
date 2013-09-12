from spacefinder import app
import json
import datetime
from flask import (Blueprint, request, redirect,
                   render_template, session, abort)
from models import Listing


views = Blueprint('spacefinder_views', __name__)


@app.template_filter('currency')
def format_currency(value):
    return "${:,.0f}".format(value)


@views.route('/')
def index():
    listings = Listing.query.all()
    return render_template('index.html', listings=listings)
