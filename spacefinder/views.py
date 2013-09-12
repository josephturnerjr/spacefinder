from spacefinder import app
import json
import datetime
from flask import (Blueprint, request, redirect,
                   render_template, session, abort)


views = Blueprint('spacefinder_views', __name__)


@app.template_filter('currency')
def format_currency(value):
    return "${:,.0f}".format(value)


@views.route('/')
def index():
    return render_template('index.html')
