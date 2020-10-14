from datetime import datetime, timedelta
from os import urandom
from pathlib import Path
from tempfile import gettempdir


def generate_secret_key(
    secret_key_filename: str, expiry_delta: timedelta = None
) -> bytes:
    secret_key_file = Path(gettempdir()) / secret_key_filename
    secret_exists = secret_key_file.exists()

    expired = None
    if secret_exists and expiry_delta is not None:
        modified_date = datetime.fromtimestamp(secret_key_file.stat().st_mtime)
        expired = datetime.now() - modified_date >= expiry_delta

    if not secret_exists or expired:
        secret_key = urandom(24)
        with secret_key_file.open("wb") as f:
            f.write(secret_key)
    else:
        with secret_key_file.open("rb") as f:
            secret_key = f.read()

    return secret_key
