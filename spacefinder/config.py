class Config(object):
    SECRET_KEY = 'YOUR_SECRET_KEY'  # FILL IN YOUR SECRET KEY
    # The domain configuration point is used both for Google Analytics
    #   as well as for the 'from' address for outgoing emails
    DOMAIN = 'example.com'  # Fill in the domain name this is hosted on
    GOOGLE_ANALYTICS_API_KEY = 'YOUR_GA_API_KEY'  # Fill in your GA key
    GOOGLE_MAPS_API_KEY = 'YOUR_GM_API_KEY'  # Fill in your GM key
    MAILGUN_API_KEY = 'YOUR_MG_API_KEY'  # Fill in your mailgun key


class ProductionConfig(Config):
    pass


class DevConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/test.db'
