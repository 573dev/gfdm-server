# V8 Server
[![Python Version](https://img.shields.io/badge/python-3.8-blue.svg)](https://www.python.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

Simlated eAmuse Server for GFDM V8 (maybe also V7 in the future?)

## Development

To run this in development mode, you should do the following:

```python
# Create a venv and install the package
python -m venv venv
. venv/bin/activate
pip install --upgrade pip
pip install -e .

# Set the development environment variables
export FLASK_APP=v8_server
export FLASK_ENV=development

# Run the server
flask run
```
