import logging
import os
from logging.config import dictConfig
from pathlib import Path
from typing import Optional, Union

from flask import Flask, has_request_context, request

from v8_server.config import Development, Production
from v8_server.utils.flask import generate_secret_key

from .version import __version__


class RequestFormatter(logging.Formatter):
    def format(self, record):
        encrypted = "None"
        compressed = "None"
        method = None

        if has_request_context():
            method = request.method
            headers = request.headers

            if "x-eamuse-info" in headers:
                encrypted = headers["x-eamuse-info"]
            if "x-compress" in headers:
                compressed = headers["x-compress"]

        record.encrypted = encrypted
        record.compressed = "None" if compressed == "none" else compressed
        record.method = method

        return super().format(record)


# Define the logger
dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[ %(asctime)s | %(levelname)-8s | %(name)s ]\n%(message)s"
            },
            "detailed": {
                "()": RequestFormatter,
                "format": (
                    "[ %(asctime)s | %(levelname)-8s | %(method)-4s | %(encrypted)-15s "
                    "| %(compressed)-4s | %(name)s ]\n%(message)s"
                ),
            },
        },
        "handlers": {
            "wsgi": {
                "class": "logging.StreamHandler",
                "stream": "ext://flask.logging.wsgi_errors_stream",
                "formatter": "default",
            },
            "debugfile": {
                "class": "logging.handlers.TimedRotatingFileHandler",
                "filename": "logs/debug.log",
                "formatter": "default",
                "when": "midnight",
            },
            "requestsfile": {
                "class": "logging.handlers.TimedRotatingFileHandler",
                "filename": "logs/requests.log",
                "formatter": "detailed",
                "when": "midnight",
            },
            "allfile": {
                "class": "logging.handlers.TimedRotatingFileHandler",
                "filename": "logs/all.log",
                "formatter": "detailed",
                "when": "midnight",
            },
            "werkzeugfile": {
                "class": "logging.handlers.TimedRotatingFileHandler",
                "filename": "logs/werkzeug.log",
                "formatter": "detailed",
                "when": "midnight",
            },
        },
        "loggers": {
            "": {"handlers": ["wsgi", "allfile"]},
            "v8_server": {"level": "DEBUG", "handlers": ["debugfile"]},
            "requests": {"level": "DEBUG", "handlers": ["requestsfile"]},
            "werkzeug": {"level": "DEBUG", "handlers": ["werkzeugfile"]},
        },
    }
)
logging.getLogger("").setLevel(logging.INFO)

# Set the proper config values
config: Optional[Union[Production, Development]] = None
if os.environ.get("ENV", "dev") == "prod":
    config = Production()
else:
    config = Development()
    print(" * THIS APP IS IN DEV MODE")

# Set the location for the static files and templates
# We might not even need this?
package_dir = Path(__file__).parent / "view"
template_dir = str(package_dir / "templates")
static_dir = str(package_dir / "static")

# Initialize the flask app
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
app.secret_key = generate_secret_key(config.SECRET_KEY_FILENAME)
app.config.from_object(config)

# We need to import the views here specifically once the flask app has been initialized
import v8_server.view  # noqa: F401, E402


__all__ = ["__version__", "app"]
