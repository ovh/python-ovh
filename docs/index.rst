.. Python-OVH documentation master file, created by
   sphinx-quickstart on Tue Aug 26 13:44:18 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root ``toctree`` directive.

Python-OVH: lightweight wrapper around OVH's APIs
=================================================

Thin wrapper around OVH's APIs. Handles all the hard work including credential
creation and requests signing.

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

API Documentation
=================

.. toctree::
   :maxdepth: 2
   :glob:

   api/ovh/*

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

See Configuration_ for more inforamtions on available configuration mechanisms.

.. note:: When using a versioning system, make sure to add ``ovh.conf`` to ignored
          files. It contains confidential/security-sensitive informations!

3. Authorize your application to access a customer account
**********************************************************

To allow your application to access a customer account using the API on your
behalf, you need a **consumer key (CK)**.

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

Install a new mail redirection
------------------------------

e-mail redirections may be freely configured on domains and DNS zones hosted by
OVH to an arbitrary destination e-mail using API call
``POST /email/domain/{domain}/redirection``.

For this call, the api specifies that the source adress shall be given under the
``from`` keyword. Which is a problem as this is also a reserved Python keyword.
In this case, simply prefix it with a '_', the wrapper will automatically detect
it as being a prefixed reserved keyword and will subsitute it. Such aliasing
is only supported with reserved keywords.

.. code:: python

    # -*- encoding: utf-8 -*-

    import ovh

    DOMAIN = "example.com"
    SOURCE = "sales@example.com"
    DESTINATION = "contact@example.com"

    # create a client
    client = ovh.Client()

    # Create a new alias
    client.post('/email/domain/%s/redirection' % DOMAIN,
            _from=SOURCE,
            to=DESTINATION
            localCopy=False
        )
    print "Installed new mail redirection from %s to %s" % (SOURCE, DESTINATION)

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

    # create a client without a consumerKey
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

Configuration
=============

The straightforward way to use OVH's API keys is to embed them directly in the
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

Passing parameters
==================

You can call all the methods of the API with the necessary arguments.

If an API needs an argument colliding with a Python reserved keyword, it
can be prefixed with an underscore. For example, ``from`` argument of
``POST /email/domain/{domain}/redirection`` may be replaced by ``_from``.

With characters invalid in python argument name like a dot, you can:

.. code:: python

    # -*- encoding: utf-8 -*-

    import ovh

    params = {}
    params['date.from'] = '2014-01-01'
    params['date.to'] = '2015-01-01'

    # create a client
    client = ovh.Client()

    # pass parameters using **
    client.post('/me/bills', **params)

Advanced usage
==============

Un-authenticated calls
----------------------

If the user has not authenticated yet (ie, there is no valid Consumer Key), you
may force ``python-ovh`` to issue the call by passing ``_need_auth=True`` to
the high level ``get()``, ``post()``, ``put()`` and ``delete()`` helpers or
``need_auth=True`` to the low level method ``Client.call()`` and
``Client.raw_call()``.

This is needed when calling ``POST /auth/credential`` and ``GET /auth/time``
which are used internally for authentication and can optionally be done for
most of the ``/order`` calls.

Access the raw requests response objects
----------------------------------------

The high level ``get()``, ``post()``, ``put()`` and ``delete()`` helpers as well
as the lower level ``call()`` will returned a parsed json response or raise in
case of error.

In some rare scenario, advanced setups, you may need to perform customer
processing on the raw request response. It may be accessed via ``raw_call()``.
This is the lowest level call in ``python-ovh``. See the source for more
informations.

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

Related links
=============

- **contribute**: https://github.com/ovh/python-ovh
- **Report bugs**: https://github.com/ovh/python-ovh/issues
- **Download**: http://pypi.python.org/pypi/ovh
