.. image:: https://github.com/ovh/python-ovh/raw/master/docs/img/logo.png
           :alt: Python & OVH APIs
           :target: https://pypi.python.org/pypi/ovh

Lightweight wrapper around OVH's APIs. Handles all the hard work including
credential creation and requests signing.

.. image:: https://img.shields.io/pypi/v/ovh.svg
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

Use the API on behalf of a user
-------------------------------

1. Create an application
************************

To interact with the APIs, the SDK needs to identify itself using an
``application_key`` and an ``application_secret``. To get them, you need
to register your application. Depending the API you plan yo use, visit:

- `OVH Europe <https://eu.api.ovh.com/createApp/>`_
- `OVH North-America <https://ca.api.ovh.com/createApp/>`_
- `RunAbove <https://api.runabove.com/createApp/>`_

Once created, you will obtain an **application key (AK)** and an **application
secret (AS)**.

2. Configure your application
*****************************

The easiest and safest way to use your application's credentials is create an
``ovh.conf`` configuration file in application's working directory. Here is how
it looks like:

.. code:: ini

    [default]
    ; general configuration: default endpoint
    endpoint=ovh-eu

    [ovh-eu]
    ; configuration specific to 'ovh-eu' endpoint
    application_key=my_app_key
    application_secret=my_application_secret
    ; uncomment following line when writing a script application
    ; with a single consumer key.
    ;consumer_key=my_consumer_key

Depending on the API you want to use, you may set the ``endpoint`` to:

* ``ovh-eu`` for OVH Europe API
* ``ovh-ca`` for OVH North-America API
* ``runabove-ca`` for RunAbove API

See Configuration_ for more inforamtions on available configuration mechanisms.

.. note:: When using a versioning system, make sure to add ``ovh.conf`` to ignored
          files. It contains confidential/security-sensitive informations!

3. Authorize your application to access a customer account
**********************************************************

To allow your application to access a customer account using the API on your
behalf, you need a **consumer key (CK)**.

Here is a sample code you can use to allow your application to access a
customer's informations:

.. code:: python

    # -*- encoding: utf-8 -*-

    import ovh

    # create a client using configuration
    client = ovh.Client()

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

.. note:: To request full and unlimited access to the API, you may use wildcards:

.. code:: python

    access_rules = [
        {'method': 'GET', 'path': '/*'},
        {'method': 'POST', 'path': '/*'},
        {'method': 'PUT', 'path': '/*'},
        {'method': 'DELETE', 'path': '/*'}
    ]

Grab bill list
--------------

Let's say you want to integrate OVH bills into your own billing system, you
could just script around the ``/me/bills`` endpoints and even get the details
of each bill lines using ``/me/bill/{billId}/details/{billDetailId}``.

This example assumes an existing Configuration_ with valid ``application_key``,
``application_secret`` and ``consumer_key``.

.. code:: python

    # -*- encoding: utf-8 -*-

    import ovh

    # create a client
    client = ovh.Client()

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

'Network burst' is a free service but is opt-in. What if you have, say, 10
servers in ``SBG-1`` datacenter? You certainely don't want to activate it
manually for each servers. You could take advantage of a code like this.

This example assumes an existing Configuration_ with valid ``application_key``,
``application_secret`` and ``consumer_key``.

.. code:: python

    # -*- encoding: utf-8 -*-

    import ovh

    # create a client
    client = ovh.Client()

    # get list of all server names
    servers = client.get('/dedicated/server/')

    # find all servers in SBG-1 datacenter
    for server in servers:
        details = client.get('/dedicated/server/%s' % server)
        if details['datacenter'] == 'sbg1':
            # enable burst on server
            client.put('/dedicated/server/%s/burst' % server, status='active')
            print "Enabled burst for %s server located in SBG-1" % server

List application authorized to access your account
--------------------------------------------------

Thanks to the application key / consumer key mechanism, it is possible to
finely track applications having access to your data and revoke this access.
This examples lists validated applications. It could easily be adapted to
manage revocation too.

This example assumes an existing Configuration_ with valid ``application_key``,
``application_secret`` and ``consumer_key``.

.. code:: python

    # -*- encoding: utf-8 -*-

    import ovh
    from tabulate import tabulate

    # create a client
    client = ovh.Client()

    credentials = client.get('/me/api/credential', status='validated')

    # pretty print credentials status
    table = []
    for credential_id in credentials:
        credential_method = '/me/api/credential/'+str(credential_id)
        credential = client.get(credential_method)
        application = client.get(credential_method+'/application')

        table.append([
            credential_id,
            '[%s] %s' % (application['status'], application['name']),
            application['description'],
            credential['creation'],
            credential['expiration'],
            credential['lastUse'],
        ])
    print tabulate(table, headers=['ID', 'App Name', 'Description',
                                   'Token Creation', 'Token Expiration', 'Token Last Use'])

Before running this example, make sure you have the
`tabulate <https://pypi.python.org/pypi/tabulate>`_ library installed. It's a
pretty cool library to pretty print tabular data in a clean and easy way.

>>> pip install tabulate

List Runabove's instance
------------------------

This example assumes an existing Configuration_ with valid ``application_key``,
``application_secret`` and ``consumer_key``.

.. code:: python

    # -*- encoding: utf-8 -*-

    import ovh
    from tabulate import tabulate

    # visit https://api.runabove.com/createApp/ to create your application's credentials
    client = ovh.Client(endpoint='runabove-ca')

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
pretty cool library to pretty print tabular data in a clean and easy way.

>>> pip install tabulate

Configuration
=============

The straightfoward way to use OVH's API keys is to embed them directly in the
application code. While this is very convenient, it lacks of elegance and
flexibility.

Alternatively it is suggested to use configuration files or environment
variables so that the same code may run seamlessly in multiple environments.
Production and development for instance.

This wrapper will first look for direct instanciation parameters then
``OVH_ENDPOINT``, ``OVH_APPLICATION_KEY``, ``OVH_APPLICATION_SECRET`` and
``OVH_CONSUMER_KEY`` environment variables. If either of these parameter is not
provided, it will look for a configuration file of the form:

.. code:: ini

    [default]
    ; general configuration: default endpoint
    endpoint=ovh-eu

    [ovh-eu]
    ; configuration specific to 'ovh-eu' endpoint
    application_key=my_app_key
    application_secret=my_application_secret
    consumer_key=my_consumer_key

The client will successively attempt to locate this configuration file in

1. Current working directory: ``./ovh.conf``
2. Current user's home directory ``~/.ovh.conf``
3. System wide configuration ``/etc/ovh.conf``

This lookup mechanism makes it easy to overload credentials for a specific
project or user.

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
- **Create script credentials** (all keys at once): https://eu.api.ovh.com/createToken/

OVH North America
-----------------

- **Documentation**: https://ca.api.ovh.com/
- **Community support**: api-subscribe@ml.ovh.net
- **Console**: https://ca.api.ovh.com/console
- **Create application credentials**: https://ca.api.ovh.com/createApp/
- **Create script credentials** (all keys at once): https://ca.api.ovh.com/createToken/

Runabove
--------

- **Community support**: https://community.runabove.com/
- **Console**: https://api.runabove.com/console/
- **Create application credentials**: https://api.runabove.com/createApp/
- **High level SDK**: https://github.com/runabove/python-runabove
- **Create script credentials** (all keys at once): https://api.runabove.com/createToken/

Related links
=============

- **Contribute**: https://github.com/ovh/python-ovh
- **Report bugs**: https://github.com/ovh/python-ovh/issues
- **Download**: http://pypi.python.org/pypi/ovh

