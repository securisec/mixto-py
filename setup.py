# pylint: disable=undefined-variable
import sys
from setuptools import setup, find_packages
from os import path

# get version and author information
with open("mixto/__version__.py", "r") as f:
    exec(f.read())


def read_requirements():
    with open("requirements.txt") as f:
        return f.read().splitlines()


requirements = read_requirements()

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), "r", encoding="utf8") as f:
    long_description = f.read()

setup(
    long_description=long_description,
    long_description_content_type="text/markdown",
    name="mixto-py",
    license="GPL",
    version=__version__,
    author=__author__,
    url="https://github.com/securisec/mixto-py",
    project_urls={
        "Documentation": "https://mixto-py.readthedocs.io/en/latest/",
        "Source Code": "https://github.com/securisec/mixto-py",
    },
    packages=find_packages(exclude=(["tests", "docs"])),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3.7",
    ],
    python_requires=">=3.6",
)
