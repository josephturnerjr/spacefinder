class Config(object):
    SECRET_KEY = '' 


class ProductionConfig(Config):
    pass


class DevConfig(Config):
    DEBUG = True
