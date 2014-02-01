from flask import Flask, render_template
import os

env = os.environ.get('ENVIRONMENT_TYPE', 'dev')
app = Flask(__name__)
try:
    app.config.from_object('spacefinder.config.%sConfig' % env.capitalize())
except:
    print "Unable to import the configuration file. This is most likely because you have yet to create a config.py file."
    print "See example.config.py for more instructions."
    sys.exit(0)


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


from spacefinder.views import views
from spacefinder.admin_views import views as admin_views
from spacefinder.db_functions import init_db
app.register_blueprint(views)
app.register_blueprint(admin_views, url_prefix='/admin')
