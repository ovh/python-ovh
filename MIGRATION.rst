############################
Migrate from legacy wrappers
############################

This guide specifically targets developers coming from the legacy wrappers
previously distributed on https://api.ovh.com/g934.first_step_with_api. It
highlights the main evolutions between these 2 major version as well as some
tips to help with the migration. If you have any further questions, feel free
to drop a mail on api@ml.ovh.net (api-subscribe@ml.ovh.net to subscribe).

Installation
============

Legacy wrappers were distributed as zip files for direct integration into
final projects. This new version is fully integrated with Python's standard
distribution channels.

Recommended way to add ``python-ovh`` to a project: add ``ovh`` to a
``requirements.txt`` file ate the root of the project.

.. code::

    # file: requirements.txt
    ovh # add '==0.2.0' to force 0.2.0 version


To refresh the dependencies, just run:

.. code:: bash

    pip install -r requirements.txt

Usage
=====

Import and the client class
---------------------------

Legacy method:
**************

.. code:: python

    from OvhApi import Api, OVH_API_EU, OVH_API_CA

New method:
***********

.. code:: python

    from ovh import Client

Instantiate a new client
------------------------

Legacy method:
**************

.. code:: python

    client = Api(OVH_API_EU, 'app key', 'app secret', 'consumer key')

New method (*compatibility*):
*****************************

.. code:: python

    client = Client('ovh-eu', 'app key', 'app secret', 'consumer key')

Similarly, ``OVH_API_CA`` has been replaced by ``'ovh-ca'``.

New method (*compatibility*):
*****************************

To avoid embedding credentials in a project, this new version introduced a new
configuration mechanism using either environment variables or configuration
files.

In a Nutshell, you may put your credentials in a file like ``/etc/ovh.conf`` or
``~/.ovh.conf`` like this one:

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

And then simply create a client instance:

.. code:: python

    from ovh import Client
    client = Client()

With no additional boilerplate!

For more information on available configuration mechanism, please see
https://github.com/ovh/python-ovh/blob/master/README.rst#configuration

Use the client
--------------

Legacy method:
**************

.. code:: python

    # API helpers
    data = client.get('/my/method?filter_1=value_1&filter_2=value_2')
    data = client.post('/my/method', {'param_1': 'value_1', 'param_2': 'value_2'})
    data = client.put('/my/method', {'param_1': 'value_1', 'param_2': 'value_2'})
    data = client.delete('/my/method')

    # Advanced, low level call
    data = client.rawCall('GET', '/my/method?my_filter=my_value', content=None)

New method (*compatibility*):
*****************************

.. code:: python

    # API helpers
    data = client.get('/my/method?filter_1=value_1&filter_2=value_2')
    data = client.post('/my/method', **{'param_1': 'value_1', 'param_2': 'value_2'})
    data = client.put('/my/method', **{'param_1': 'value_1', 'param_2': 'value_2'})
    data = client.delete('/my/method')

    # Advanced, low level call
    data = client.rawCall('GET', '/my/method?my_filter=my_value', data=None)


New method (*recommended*):
***************************

.. code:: python

    # API helpers
    data = client.get('/my/method', filter_1='value_1', filter_2='value_2')
    data = client.post('/my/method', param_1='value_1', param_2='value_2')
    data = client.put('/my/method', param_1='value_1', param_2='value_2')
    data = client.delete('/my/method')

    # Advanced, low level call
    data = client.rawCall('GET', '/my/method?my_filter=my_value', data=None)

