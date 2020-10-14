import codecs
from os.path import abspath, dirname, join

from setuptools import find_packages, setup


TEST_DEPS = ["coverage[toml]", "pytest", "pytest-cov"]
DOCS_DEPS = ["sphinx", "sphinx-rtd-theme", "sphinx-autoapi", "recommonmark"]
CHECK_DEPS = ["isort", "flake8", "flake8-quotes", "pep8-naming", "mypy", "black"]
REQUIREMENTS = [
    "flask",
    "watchdog",
    "pyopenssl",
    "lxml",
    "pycryptodome",
    "lzss",
    "kbinxml",
]

EXTRAS = {
    "test": TEST_DEPS,
    "docs": DOCS_DEPS,
    "check": CHECK_DEPS,
    "dev": TEST_DEPS + DOCS_DEPS + CHECK_DEPS,
}

# Read in the version
with open(join(dirname(abspath(__file__)), "VERSION")) as version_file:
    version = version_file.read().strip()


setup(
    name="V8 Server",
    version=version,
    description="Simlated eAmuse Server for GFDM V8",
    long_description=codecs.open("README.md", "r", "utf-8").read(),
    long_description_content_type="text/markdown",
    author="573dev",
    url="https://github.com/573dev/gfdm_server",
    packages=find_packages(exclude=["tests"]),
    install_requires=REQUIREMENTS,
    classifiers=[
        "Environment :: Console",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
    ],
    platforms=["any"],
    include_package_data=True,
    tests_require=TEST_DEPS,
    extras_require=EXTRAS,
)
