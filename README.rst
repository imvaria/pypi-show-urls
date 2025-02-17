pypi-show-urls
==============

Shows information about where packages come from


Installation
------------

.. code:: bash

    $ pip install pypi-show-urls


Usage
-----

.. code:: bash

    # Show all the counts for a bunch of packages
    $ pypi-show-urls -p package1 package2 package3

    # Show all the counts for a set of packages owned by users
    $ pypi-show-urls -u user1 user2 user3

    # Show all the counts for a set of packages in a list of requirements files
    $ pypi-show-urls -r requirements.txt requirements-dev.txt

    # Show all the urls found and all the versions available
    $ pypi-show-urls -v -p package1 package2 package3
    $ pypi-show-urls -v -u user1 user2 user3
    $ pypi-show-urls -v -r requirements.txt requirements-dev.txt

    # Show all the counts for a bunch of packages in a private repository
    $ pypi-show-urls -i https://private.example.com/pypi -p package1 package2 package3
