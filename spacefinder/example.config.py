class Config(object):
    ## Session secret key. This should be a random binary string. ##
    #   Do this to get a good'n:
    # >>> import os
    # >>> os.urandom(24)
    SECRET_KEY = 'YOUR_SECRET_KEY'

    # The domain configuration point is used both for Google Analytics
    #   as well as for the 'from' address for outgoing emails
    DOMAIN = 'example.com'  # Fill in the domain name this is hosted on

    GOOGLE_MAPS_API_KEY = 'YOUR_GM_API_KEY'  # Fill in your GM key

    MAILGUN_API_KEY = 'YOUR_MG_API_KEY'  # Fill in your mailgun key
    ## Optional; use a different domain for your Mailgun account
    ##   This will fall back to DOMAIN if unset
    # MAILGUN_DOMAIN = example.mailgun.org

    ## Where do you want the images stored?
    ## Make sure to create this directory
    IMG_STORAGE = '/tmp/shots'
    MAX_CONTENT_LENGTH = 4 * 1024 * 1024

    ## Database URI for sqlalchemy. SQLite is the easiest...
    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/test.db'

    ## Google tracking info
    ## This is optional, but will configure Google Analytics...
    # GOOGLE_ANALYTICS_API_KEY = 'YOUR_GA_API_KEY'
    ## ... and Google Webmaster Tools
    # GOOGLE_WEBMASTER_CODE = 'YOUR_WEBMASTER_META_VERIFICATION_TAG'


class ProductionConfig(Config):
    pass


class DevConfig(Config):
    DEBUG = True
