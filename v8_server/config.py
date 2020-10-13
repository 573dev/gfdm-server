class Config(object):
    DEBUG = False
    TESTING = False
    DB_SERVER = "localhost"
    SECRET_KEY_FILENAME = "v8_server.key"


class Development(Config):
    DEBUG = True
    SECRET_KEY_FILENAME = "dev_v8_server.key"


class Production(Config):
    pass
