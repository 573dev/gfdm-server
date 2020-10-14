class Config(object):
    DEBUG: bool = False
    TESTING: bool = False
    DB_SERVER: str = "localhost"
    SECRET_KEY_FILENAME: str = "v8_server.key"


class Development(Config):
    DEBUG: bool = True
    SECRET_KEY_FILENAME: str = "dev_v8_server.key"


class Production(Config):
    pass
