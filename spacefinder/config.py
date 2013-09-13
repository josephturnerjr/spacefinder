class Config(object):
    SECRET_KEY = 'abc' 


class ProductionConfig(Config):
    pass


class DevConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/test.db'
