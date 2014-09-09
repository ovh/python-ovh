Python-OVH: lightweight wrapper around OVH's APIs
=================================================

.. image:: http://img.shields.io/pypi/v/ovh.svg
           :alt: PyPi Version
           :target: https://pypi.python.org/pypi/ovh
.. image:: https://travis-ci.org/ovh/python-ovh.svg?branch=master
           :alt: Build Status
           :target: https://travis-ci.org/ovh/python-ovh
.. image:: https://coveralls.io/repos/ovh/python-ovh/badge.png
           :alt: Coverage Status
           :target: https://coveralls.io/r/ovh/python-ovh

Thin wrapper around OVH's APIs. Handles all the hard work including credential
creation and requests signing.

A note on authentication
------------------------

OVH's APIs relies on an OAuth based mechanism for authentication. OAuth is a
standard protocol allowing to securely authenticate both an application and a
user within an application. It also supports specific access restrictions. This
is accomplished using a set of 3 Keys:

- ``application_key``: Uniquely identifies an application. It can be seen as an
  application "login" and is attached to an account. This key may safely be
  shared.
- ``application_secret``: Authenticates application identified by
  ``application_key``. It can be seen as an application "password" and should be
  protected as such !
- ``consumer_key``: Each application's user has it's own ``consumer_key``
  specific to the this application. A ``consumer_key`` may only be valid for a
  subset of the API and a restricted amount of time.

``application_key`` and ``application_secret`` are defined once for each
application (see "Supported APIs" bellow) and ``consumer_key`` are granted once
for each application's and-user.


Installation
============

The easiest way to get the latest stable release is to grab it from `pypi
<https://pypi.python.org/pypi/ovh>`_ using ``pip``.

.. code:: bash

    pip install ovh

Alternatively, you may get latest development version directly from Git.

.. code:: bash

    pip install -e git+https://github.com/ovh/python-ovh.git#egg=ovh


Hacking
=======

This wrapper uses standard Python tools, so you should feel familiar with it.
Here is a quick outline of what it may look like. A good practice is to run
this from a ``virtualenv``.

.. code:: bash

    git clone https://github.com/ovh/python-ovh.git
    cd python-ovh
    python setup.py develop
    pip install -r requirements-dev.txt
    nostests # 100% coverage is a hard minimum


You've developed a new cool feature ? Fixed an annoying bug ? We'd be happy
to here from you !

Building documentation
======================

Documentation is managed using the excelent ``Sphinx`` system. For example, to
build HTML documentation:

.. code:: bash

    cd python-ovh/docs
    make html

Example Usage
=============

Login as a user
---------------

To communicate with APIs, the SDK uses a token on each request to identify the
user. This token is called ``consumer_key``. Getting a ``consumer_key`` is done
in 3 steps:

1. application requests a new consumer key and specifies requested access permissions.
2. application redirects user to a specific validation URL.
3. end-user authenticates himself using his OVH credentials to validate it.

Example:

.. code:: python

    # -*- encoding: utf-8 -*-

    import ovh

    # visit https://api.ovh.com/createApp/ to create your application's credentials
    APPLICATION_KEY = '<application key>'
    APPLICATION_SECRET = '<application secret>'

    # create a client without a consumerKey
    client = ovh.Client(
        endpoint='ovh-eu',
        application_key=APPLICATION_KEY,
        application_secret=APPLICATION_SECRET,
    )

    # Request RO, /me API access
    access_rules = [
        {'method': 'GET', 'path': '/me'},
    ]

    # Request token
    validation = client.request_consumerkey(access_rules)

    print "Please visit %s to authenticate" % validation['validationUrl']
    raw_input("and press Enter to continue...")

    # Print nice welcome message
    print "Welcome", client.get('/me')['firstname']
    print "Btw, your 'consumerKey' is '%s'" % validation['consumerKey']


Returned ``consumerKey`` should then be kept to avoid re-authenticating your
end-user on each use.

Note: to request full and unlimited access to the API, you may use wildcards:

.. code:: python

    access_rules = [
        {'method': 'GET', 'path': '/*'},
        {'method': 'POST', 'path': '/*'},
        {'method': 'PUT', 'path': '/*'},
        {'method': 'DELETE', 'path': '/*'}
    ]


Grab bill list
--------------

.. code:: python

    # -*- encoding: utf-8 -*-

    import ovh

    APPLICATION_KEY = '<application key>'
    APPLICATION_SECRET = '<application secret>'

    # create a client without a consumerKey
    client = ovh.Client(
        endpoint='ovh-eu',
        application_key=APPLICATION_KEY,
        application_secret=APPLICATION_SECRET,
    )

    # Request RO, /me/bill API access
    access_rules = [
        {'method': 'GET', 'path': '/me/bill'},
        {'method': 'GET', 'path': '/me/bill/*'},
    ]

    # Request token
    validation = client.request_consumerkey(access_rules)

    print "Please visit", validation['validationUrl'], "to authenticate"
    raw_input("and press Enter to continue...")

    # Grab bill list
    bills = client.get('/me/bill')
    for bill in bills:
        details = client.get('/me/bill/%s' % bill)
        print "%12s (%s): %10s --> %s" % (
            bill,
            details['date'],
            details['priceWithTax']['text'],
            details['pdfUrl'],
        )

Enable network burst in SBG1
----------------------------

.. code:: python

    # -*- encoding: utf-8 -*-

    import ovh

    # visit https://api.ovh.com/createApp/ to create your application's credentials
    APPLICATION_KEY = '<application key>'
    APPLICATION_SECRET = '<application secret>'
    CONSUMER_KEY = '<consumer key (see above)>'

    # create a client
    client = ovh.Client(
        endpoint='ovh-eu',
        application_key=APPLICATION_KEY,
        application_secret=APPLICATION_SECRET,
        consumer_key=CONSUMER_KEY,
    )

    # get list of all server names
    servers = client.get('/dedicated/server/')

    # find all servers in SBG-1 datacenter
    for server in servers:
        details = client.get('/dedicated/server/%s' % server)
        if details['datacenter'] == 'sbg1':
            # enable burst on server
            client.put('/dedicated/server/%s/burst' % server, status='active')
            print "Enabled burst for %s server located in SBG-1" % server

List Runabove's instance
------------------------

.. code:: python

    # -*- encoding: utf-8 -*-

    import ovh
    from tabulate import tabulate

    # visit https://api.runabove.com/createApp/ to create your application's credentials
    APPLICATION_KEY = '<application key>'
    APPLICATION_SECRET = '<application secret>'
    CONSUMER_KEY = '<consumer key (see above)>'

    # create a client
    client = ovh.Client(
        endpoint='runabove-ca',
        application_key=APPLICATION_KEY,
        application_secret=APPLICATION_SECRET,
        consumer_key=CONSUMER_KEY,
    )

    # get list of all instances
    instances = client.get('/instance')

    # pretty print instances status
    table = []
    for instance in instances:
        table.append([
            instance['name'],
            instance['ip'],
            instance['region'],
            instance['status'],
        ])
    print tabulate(table, headers=['Name', 'IP', 'Region', 'Status'])

Before running this example, make sure you have the
`tabulate <https://pypi.python.org/pypi/tabulate>`_ library installed. It's a
pretty cool library to pretty print tabular data.

>>> pip install tabulate

Supported APIs
==============

OVH
---

 - **documentation**: https://api.ovh.com/
 - **community support**: api-subscribe@ml.ovh.net
 - **console**: https://api.ovh.com/console
 - **get application credentials**: https://api.ovh.com/createApp/

Runabove
--------

 - **console**: https://api.runabove.com/console/
 - **get application credentials**: https://api.runabove.com/createApp/
 - **high level SDK**: https://github.com/runabove/python-runabove

Related links
=============

- **contribute**: https://github.com/ovh/python-ovh
- **Report bugs**: https://github.com/ovh/python-ovh/issues
- **Download**: http://pypi.python.org/pypi/ovh
