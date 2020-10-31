from pathlib import Path


DEV_DB_PATH = Path(__file__).parent.parent / "database"
PROD_DB_PATH = Path("/var/db")


class Config(object):
    DEBUG: bool = False
    TESTING: bool = False
    DB_SERVER: str = "localhost"
    SECRET_KEY_FILENAME: str = "v8_server.key"
    SQLALCHEMY_DATABASE_URI: str = f"sqlite+pysqlite:///{ PROD_DB_PATH / 'v8.db'}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class Development(Config):
    DEBUG: bool = True
    SECRET_KEY_FILENAME: str = "dev_v8_server.key"
    SQLALCHEMY_DATABASE_URI: str = f"sqlite+pysqlite:///{ DEV_DB_PATH / 'v8_dev.db'}"


class Production(Config):
    pass
