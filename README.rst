.. image:: https://github.com/ovh/python-ovh/raw/master/docs/img/logo.png
           :alt: Python & OVH APIs
           :target: https://pypi.python.org/pypi/ovh

Lightweight wrapper around OVH's APIs. Handles all the hard work including
credential creation and requests signing.

.. image:: http://img.shields.io/pypi/v/ovh.svg
           :alt: PyPi Version
           :target: https://pypi.python.org/pypi/ovh
.. image:: https://travis-ci.org/ovh/python-ovh.svg?branch=master
           :alt: Build Status
           :target: https://travis-ci.org/ovh/python-ovh
.. image:: https://coveralls.io/repos/ovh/python-ovh/badge.png
           :alt: Coverage Status
           :target: https://coveralls.io/r/ovh/python-ovh

.. code:: python

    # -*- encoding: utf-8 -*-

    import ovh

    # Instantiate. Visit https://api.ovh.com/createToken/index.cgi?GET=/me
    # to get your credentials
    client = ovh.Client(
        endpoint='ovh-eu',
        application_key='<application key>',
        application_secret='<application secret>',
        consumer_key='<consumer key>',
    )

    # Print nice welcome message
    print "Welcome", client.get('/me')['firstname']


Installation
============

The easiest way to get the latest stable release is to grab it from `pypi
<https://pypi.python.org/pypi/ovh>`_ using ``pip``.

.. code:: bash

    pip install ovh

Alternatively, you may get latest development version directly from Git.

.. code:: bash

    pip install -e git+https://github.com/ovh/python-ovh.git#egg=ovh

Example Usage
=============

Login as a user
---------------

1. Create an application
************************

To interact with the APIs, the SDK needs to identify itself using an
``application_key`` and an ``application_secret``. To get them, you need
to register your application. Depending the API you plan yo use, visit:

* `OVH Europe <https://eu.api.ovh.com/createApp/>`_
* `OVH North-America <https://ca.api.ovh.com/createApp/>`_
* `RunAbove <https://api.runabove.com/createApp/>`_

Once created, you will obtain an **application key (AK)** and an **application
secret (AS)**.

2. Authorize your application to access a customer account
**********************************************************

To allow your application to access a customer account using the API on your
behalf, you need a **consumer key (CK)**.

Depending the API you want to use, you need to specify an API endpoint:

* OVH Europe: ``ovh-eu``
* OVH North-America: ``ovh-ca``
* RunAbove: ``runabove-ca``

Here is a sample code you can use to allow your application to access a
customer's informations:

.. code:: python

    # -*- encoding: utf-8 -*-

    import ovh

    EDPOINT = '<endpoint>' # one of 'ovh-eu', 'ovh-ca', 'runabove-ca'
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

Hacking
=======

This wrapper uses standard Python tools, so you should feel at home with it.
Here is a quick outline of what it may look like. A good practice is to run
this from a ``virtualenv``.

Get the sources
---------------

.. code:: bash

    git clone https://github.com/ovh/python-ovh.git
    cd python-ovh
    python setup.py develop

You've developed a new cool feature ? Fixed an annoying bug ? We'd be happy
to hear from you !

Run the tests
-------------

Simply run ``nosetests``. It will automatically load its configuration from
``setup.cfg`` and output full coverage status. Since we all love quality, please
note that we do not accept contributions with test coverage under 100%.

.. code:: bash

    pip install -r requirements-dev.txt
    nosetests # 100% coverage is a hard minimum


Build the documentation
-----------------------

Documentation is managed using the excellent ``Sphinx`` system. For example, to
build HTML documentation:

.. code:: bash

    cd python-ovh/docs
    make html

Supported APIs
==============

OVH Europe
----------

- **Documentation**: https://eu.api.ovh.com/
- **Community support**: api-subscribe@ml.ovh.net
- **Console**: https://eu.api.ovh.com/console
- **Create application credentials**: https://eu.api.ovh.com/createApp/

OVH North America
-----------------

- **Documentation**: https://ca.api.ovh.com/
- **Community support**: api-subscribe@ml.ovh.net
- **Console**: https://ca.api.ovh.com/console
- **Create application credentials**: https://ca.api.ovh.com/createApp/

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
