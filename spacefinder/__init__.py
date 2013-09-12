from flask import Flask, render_template
import os

env = os.environ.get('ENVIRONMENT_TYPE', 'dev')
app = Flask(__name__)
app.config.from_object('spacefinder.config.%sConfig' % env.capitalize())


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


from spacefinder.views import views
app.register_blueprint(views)
