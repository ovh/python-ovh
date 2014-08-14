#############
Client Module
#############

.. currentmodule:: ovh.client

.. automodule:: ovh.client

.. autoclass:: Client

Constructor
===========

__init__
--------

.. automethod:: Client.__init__

High level helpers
==================

request_consumerkey
-------------------

.. automethod:: Client.request_consumerkey

get/post/put/delete
-------------------

Shortcuts around :py:func:`Client.call`. This is the recommended way to use the
wrapper.

For example, requesting the list of all bills would look like:

.. code:: python

    bills = client.get('/me/bills')

In a similar fashion, enabling network burst on a specific server would look
like:

.. code:: python

    client.put('/dedicated/server/%s/burst' % server_name, status='active')

:param str target: Rest Method as shown in API's console.
:param boolean need_auth: When `False`, bypass the signature process. This is
   interesting when calling authentication related method. Defaults to `True`
:param dict kwargs: (:py:func:`Client.post` and :py:func:`Client.put` only)
   all extra keyword arguments are passed as `data` dict to `call`. This is a
   syntaxic sugar to call API entrypoints using a regular method syntax.

.. automethod:: Client.get
.. automethod:: Client.post
.. automethod:: Client.put
.. automethod:: Client.delete

Low level API
=============

call
----

.. automethod:: Client.call

time_delta
----------

.. autoattribute:: Client.time_delta
