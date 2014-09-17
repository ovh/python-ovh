# -*- encoding: utf-8 -*-
#
# Copyright (c) 2013-2014, OVH SAS.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#  * Neither the name of OVH SAS nor the
#    names of its contributors may be used to endorse or promote products
#    derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY OVH SAS AND CONTRIBUTORS ````AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL OVH SAS AND CONTRIBUTORS BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
This module provides a simple python wrapper over the OVH REST API.
It handles requesting credential, signing queries...

 - To get your API keys: https://eu.api.ovh.com/createApp/
 - To get started with API: https://api.ovh.com/g934.first_step_with_api
"""

import hashlib
import urllib
import time
import json

from requests import request
from requests.exceptions import RequestException

from .config import config
from .exceptions import (
    APIError, NetworkError, InvalidResponse, InvalidRegion, InvalidKey,
    ResourceNotFoundError, BadParametersError, ResourceConflictError, HTTPError,
)

#: Mapping between OVH API region names and corresponding endpoints
ENDPOINTS = {
    'ovh-eu': 'https://eu.api.ovh.com/1.0',
    'ovh-ca': 'https://ca.api.ovh.com/1.0',
    'runabove-ca': 'https://api.runabove.com/1.0',
}


class Client(object):
    """
    Low level OVH Client. It abstracts all the authentication and request
    signing logic along with some nice tools helping with key generation.

    All low level request logic including signing and error handling takes place
    in :py:func:`Client.call` function. Convenient wrappers
    :py:func:`Client.get` :py:func:`Client.post`, :py:func:`Client.put`,
    :py:func:`Client.delete` should be used instead. :py:func:`Client.post`,
    :py:func:`Client.put` both accept arbitrary list of keyword arguments
    mapped to ``data`` param of :py:func:`Client.call`.

    Example usage:

    .. code:: python

        from ovh import Client, APIError

        REGION = 'ovh-eu'
        APP_KEY="<application key>"
        APP_SECRET="<application secret key>"
        CONSUMER_KEY="<consumer key>"

        client = Client(REGION, APP_KEY, APP_SECRET, CONSUMER_KEY)

        try:
            print client.get('/me')
        except APIError as e:
            print "Ooops, failed to get my info:", e.msg

    """

    def __init__(self, endpoint=None, application_key=None,
                 application_secret=None, consumer_key=None):
        """
        Creates a new Client. No credential check is done at this point.

        The ``application_key`` identifies your application while
        ``application_secret`` authenticates it. On the other hand, the
        ``consumer_key`` uniquely identifies your application's end user without
        requiring his personal password.

        If any of ``endpoint``, ``application_key``, ``application_secret``
        or ``consumer_key`` is not provided, this client will attempt to locate
        from them from environment, ~/.ovh.cfg or /etc/ovh.cfg.

        See :py:mod:`ovh.config` for more informations on supported
        configuration mechanisms.

        :param str endpoint: API endpoint to use. Valid values in ``ENDPOINTS``
        :param str application_key: Application key as provided by OVH
        :param str application_secret: Application secret key as provided by OVH
        :param str consumer_key: uniquely identifies
        :raises InvalidRegion: if ``endpoint`` can't be found in ``ENDPOINTS``.
        """
        # load endpoint
        if endpoint is None:
            endpoint = config.get('default', 'endpoint')

        try:
            self._endpoint = ENDPOINTS[endpoint]
        except KeyError:
            raise InvalidRegion("Unknow endpoint %s. Valid endpoints: %s",
                                endpoint, ENDPOINTS.keys())

        # load keys
        if application_key is None:
            application_key = config.get(endpoint, 'application_key')
        self._application_key = application_key

        if application_secret is None:
            application_secret = config.get(endpoint, 'application_secret')
        self._application_secret = application_secret

        if consumer_key is None:
            consumer_key = config.get(endpoint, 'consumer_key')
        self._consumer_key = consumer_key

        # lazy load time delta
        self._time_delta = None

    ## high level API

    @property
    def time_delta(self):
        """
        Request signatures are valid only for a short amount of time to mitigate
        risk of attack replay scenarii which requires to use a common time
        reference. This function queries endpoint's time and computes the delta.
        This entrypoint does not require authentication.

        This method is *lazy*. It will only load it once even though it is used
        for each request.

        .. note:: You should not need to use this property directly

        :returns: time distance between local and server time in seconds.
        :rtype: int
        """
        if self._time_delta is None:
            server_time = self.get('/auth/time', _need_auth=False)
            self._time_delta = server_time - int(time.time())
        return self._time_delta


    def request_consumerkey(self, access_rules, redirect_url=None):
        """
        Create a new "consumer key" identifying this application's end user. API
        will return a ``consumerKey`` and a ``validationUrl``. The end user must
        visit the ``validationUrl``, authenticate and validate the requested
        ``access_rules`` to link his account to the ``consumerKey``. Once this
        is done, he may optionaly be redirected to ``redirect_url`` and the
        application can start using the ``consumerKey``.

        The new ``consumerKey`` is automatically loaded into
        ``self._consumer_key`` and is ready to used as soon as validated.

        As signing requires a valid ``consumerKey``, the method does not require
        authentication, only a valid ``applicationKey``

        ``access_rules`` is a list of the form:

        .. code:: python

            # Grant full, unrestricted API access
            access_rules = [
                {'method': 'GET', 'path': '/*'},
                {'method': 'POST', 'path': '/*'},
                {'method': 'PUT', 'path': '/*'},
                {'method': 'DELETE', 'path': '/*'}
            ]

        To request a new consumer key, you may use a code like:

        .. code:: python

            # Request RO, /me API access
            access_rules = [
                {'method': 'GET', 'path': '/me'},
            ]

            # Request token
            validation = client.request_consumerkey(access_rules)

            print "Please visit", validation['validationUrl'], "to authenticate"
            raw_input("and press Enter to continue...")

            # Print nice welcome message
            print "Welcome", client.get('/me')['firstname']


        :param list access_rules: Mapping specifying requested privileges.
        :param str redirect_url: Where to redirect end user upon validation.
        :raises APIError: When ``self.call`` fails.
        :returns: dict with ``consumerKey`` and ``validationUrl`` keys
        :rtype: dict
        """
        res = self.post('/auth/credential', _need_auth=False,
                        accessRules=access_rules, redirection=redirect_url)
        self._consumer_key = res['consumerKey']
        return res

    ## API shortcuts

    def get(self, _target, _need_auth=True, **kwargs):
        """'GET' :py:func:`Client.call` wrapper"""
        if kwargs:
            query_string = urllib.urlencode(kwargs)
            if '?' in _target:
                _target = '%s&%s' % (_target, query_string)
            else:
                _target = '%s?%s' % (_target, query_string)

        return self.call('GET', _target, None, _need_auth)

    def put(self, _target, _need_auth=True, **kwargs):
        """'PUT' :py:func:`Client.call` wrapper"""
        return self.call('PUT', _target, kwargs, _need_auth)

    def post(self, _target, _need_auth=True, **kwargs):
        """'POST' :py:func:`Client.call` wrapper"""
        return self.call('POST', _target, kwargs, _need_auth)

    def delete(self, _target, _need_auth=True):
        """'DELETE' :py:func:`Client.call` wrapper"""
        return self.call('DELETE', _target, None, _need_auth)

    ## low level helpers

    def call(self, method, path, data=None, need_auth=True):
        """
        Lowest level call helper. If ``consumer_key`` is not ``None``, inject
        authentication headers and sign the request.

        Request signature is a sha1 hash on following fields, joined by '+'
         - application_secret
         - consumer_key
         - METHOD
         - full request url
         - body
         - server current time (takes time delta into account)

        :param str method: HTTP verb. Usualy one of GET, POST, PUT, DELETE
        :param str path: api entrypoint to call, relative to endpoint base path
        :param data: any json serializable data to send as request's body
        :param boolean need_auth: if False, bypass signature
        :raises HTTPError: when underlying request failed for network reason
        :raises InvalidResponse: when API response could not be decoded
        """
        body = ''
        target = self._endpoint + path
        headers = {
            'X-Ovh-Application': self._application_key
        }

        # include payload
        if data is not None:
            headers['Content-type'] = 'application/json'
            body = json.dumps(data)

        # sign request. Never sign 'time' or will recuse infinitely
        if need_auth:
            if not self._application_secret:
                raise InvalidKey("Invalid ApplicationSecret '%s'" %
                                 self._application_secret)

            if not self._consumer_key:
                raise InvalidKey("Invalid ConsumerKey '%s'" %
                                 self._consumer_key)

            now = str(int(time.time()) + self.time_delta)
            signature = hashlib.sha1()
            signature.update("+".join([
                self._application_secret, self._consumer_key,
                method.upper(), target,
                body,
                now
            ]))

            headers['X-Ovh-Consumer'] = self._consumer_key
            headers['X-Ovh-Timestamp'] = now
            headers['X-Ovh-Signature'] = "$1$" + signature.hexdigest()

        # attempt request
        try:
            result = request(method, target, headers=headers, data=body)
        except RequestException as error:
            raise HTTPError("Low HTTP request failed error", error)

        status = result.status_code

        # attempt to decode and return the response
        try:
            json_result = result.json()
        except ValueError as error:
            raise InvalidResponse("Failed to decode API response", error)

        # error check
        if status >= 100 and status < 300:
            return json_result
        elif status == 404:
            raise ResourceNotFoundError(json_result.get('message'))
        elif status == 400:
            raise BadParametersError(json_result.get('message'))
        elif status == 409:
            raise ResourceConflictError(json_result.get('message'))
        elif status == 0:
            raise NetworkError()
        else:
            raise APIError(json_result.get('message'))
