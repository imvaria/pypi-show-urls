#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name="pypi-show-urls",
    version="3.0.0",

    description="Shows all the installation candidates for a list of packages",
    long_description=open("README.rst").read(),
    url="https://github.com/imvaria/pypi-show-urls",

    author="Donald Stufft",
    author_email="donald@stufft.io",

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3'
    ],

    install_requires=[
        "html5lib",
        "requests",
    ],

    packages=find_packages(exclude=["tests"]),

    entry_points={
        "console_scripts": [
            "pypi-show-urls = pypi_show_urls.__main__:main",
        ],
    },
)
