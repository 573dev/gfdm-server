import os
from pathlib import Path
from typing import Optional, Union

from flask import Flask

from v8_server.config import Development, Production
from v8_server.utils import generate_secret_key

from .version import __version__


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
