# Copyright (c) 2013-2025, OVH SAS.
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
 - To get started with API:
 https://help.ovhcloud.com/csm/en-gb-api-getting-started-ovhcloud-api?id=kb_article_view&sysparm_article=KB0042784
"""

import hashlib
import json
import keyword
import time
from urllib.parse import urlencode

from requests import Session
from requests.exceptions import RequestException

from . import config
from .consumer_key import ConsumerKeyRequest
from .exceptions import (
    APIError,
    BadParametersError,
    Forbidden,
    HTTPError,
    InvalidConfiguration,
    InvalidCredential,
    InvalidKey,
    InvalidRegion,
    InvalidResponse,
    NetworkError,
    NotCredential,
    NotGrantedCall,
    ResourceConflictError,
    ResourceExpiredError,
    ResourceNotFoundError,
)
from .oauth2 import OAuth2

# Mapping between OVH API region names and corresponding endpoints
ENDPOINTS = {
    "ovh-eu": "https://eu.api.ovh.com/1.0",
    "ovh-us": "https://api.us.ovhcloud.com/1.0",
    "ovh-ca": "https://ca.api.ovh.com/1.0",
    "kimsufi-eu": "https://eu.api.kimsufi.com/1.0",
    "kimsufi-ca": "https://ca.api.kimsufi.com/1.0",
    "soyoustart-eu": "https://eu.api.soyoustart.com/1.0",
    "soyoustart-ca": "https://ca.api.soyoustart.com/1.0",
}

# Default timeout for each request. 180 seconds connect, 180 seconds read.
TIMEOUT = 180

# OAuth2 token provider URLs
OAUTH2_TOKEN_URLS = {
    "ovh-eu": "https://www.ovh.com/auth/oauth2/token",
    "ovh-ca": "https://ca.ovh.com/auth/oauth2/token",
    "ovh-us": "https://us.ovhcloud.com/auth/oauth2/token",
}


class Client:
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
            print(client.get('/me'))
        except APIError as e:
            print("Ooops, failed to get my info:", e.msg)

    """

    def __init__(
        self,
        endpoint=None,
        application_key=None,
        application_secret=None,
        consumer_key=None,
        timeout=TIMEOUT,
        config_file=None,
        client_id=None,
        client_secret=None,
    ):
        """
        Creates a new Client. No credential check is done at this point.

        When using OAuth2 authentication, ``client_id`` and ``client_secret``
        will be used to initiate a Client Credential OAuth2 flow.

        When using the OVHcloud authentication method, the ``application_key``
        identifies your application while ``application_secret`` authenticates
        it. On the other hand, the ``consumer_key`` uniquely identifies your
        application's end user without requiring his personal password.

        If any of ``endpoint``, ``application_key``, ``application_secret``,
        ``consumer_key``, ``client_id`` or ``client_secret`` is not provided,
        this client will attempt to locate from them from environment,
        ``~/.ovh.cfg`` or ``/etc/ovh.cfg``.

        See :py:mod:`ovh.config` for more information on supported
        configuration mechanisms.

        ``timeout`` can either be a float or a tuple. If it is a float it
        sets the same timeout for both connection and read. If it is a tuple
        connection and read timeout will be set independently. To use the
        latter approach you need at least requests v2.4.0. Default value is
        180 seconds for connection and 180 seconds for read.

        :param str endpoint: API endpoint to use. Valid values in ``ENDPOINTS``
        :param str application_key: Application key as provided by OVHcloud
        :param str application_secret: Application secret key as provided by OVHcloud
        :param str consumer_key: uniquely identifies
        :param str client_id: OAuth2 client ID
        :param str client_secret: OAuth2 client secret
        :param tuple timeout: Connection and read timeout for each request
        :param float timeout: Same timeout for both connection and read
        :raises InvalidRegion: if ``endpoint`` can't be found in ``ENDPOINTS``.
        """

        configuration = config.ConfigurationManager()

        # Load a custom config file if requested
        if config_file is not None:
            configuration.read(config_file)

        # load endpoint
        if endpoint is None:
            endpoint = configuration.get("default", "endpoint")

        try:
            self._endpoint = ENDPOINTS[endpoint]
        except KeyError:
            raise InvalidRegion("Unknown endpoint %s. Valid endpoints: %s", endpoint, ENDPOINTS.keys())

        # load keys
        if application_key is None:
            application_key = configuration.get(endpoint, "application_key")
        self._application_key = application_key

        if application_secret is None:
            application_secret = configuration.get(endpoint, "application_secret")
        self._application_secret = application_secret

        if consumer_key is None:
            consumer_key = configuration.get(endpoint, "consumer_key")
        self._consumer_key = consumer_key

        # load OAuth2 data
        if client_id is None:
            client_id = configuration.get(endpoint, "client_id")
        self._client_id = client_id

        if client_secret is None:
            client_secret = configuration.get(endpoint, "client_secret")
        self._client_secret = client_secret

        # configuration validation
        if bool(self._client_id) is not bool(self._client_secret):
            raise InvalidConfiguration("Invalid OAuth2 config, both client_id and client_secret must be given")

        if bool(self._application_key) is not bool(self._application_secret):
            raise InvalidConfiguration(
                "Invalid authentication config, both application_key and application_secret must be given"
            )

        if self._client_id is not None and self._application_key is not None:
            raise InvalidConfiguration(
                "Can't use both application_key/application_secret and OAuth2 client_id/client_secret"
            )
        if self._client_id is None and self._application_key is None:
            raise InvalidConfiguration(
                "Missing authentication information, you need to provide at least an application_key/application_secret"
                " or a client_id/client_secret"
            )
        if self._client_id and endpoint not in OAUTH2_TOKEN_URLS:
            raise InvalidConfiguration(
                "OAuth2 authentication is not compatible with endpoint "
                + endpoint
                + " (it can only be used with ovh-eu, ovh-ca and ovh-us)"
            )

        # when in OAuth2 mode, instantiate the oauthlib client
        if self._client_id:
            self._oauth2 = OAuth2(
                client_id=self._client_id,
                client_secret=self._client_secret,
                token_url=OAUTH2_TOKEN_URLS[endpoint],
            )
        else:
            self._oauth2 = None

        # lazy load time delta
        self._time_delta = None

        # use a requests session to reuse HTTPS connections between requests
        self._session = Session()

        # Override default timeout
        self._timeout = timeout

    # high level API

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
            server_time = self.get("/auth/time", _need_auth=False)
            self._time_delta = server_time - int(time.time())
        return self._time_delta

    def new_consumer_key_request(self):
        """
        Create a new consumer key request. This is the recommended way to create
        a new consumer key request.

        Full example:

        >>> import ovh
        >>> client = ovh.Client("ovh-eu")
        >>> ck = client.new_consumer_key_request()
        >>> ck.add_rules(ovh.API_READ_ONLY, "/me")
        >>> ck.add_recursive_rules(ovh.API_READ_WRITE, "/sms")
        >>> ck.request()
        {
            'state': 'pendingValidation',
            'consumerKey': 'TnpZAd5pYNqxk4RhlPiSRfJ4WrkmII2i',
            'validationUrl': 'https://eu.api.ovh.com/auth/?credentialToken=now2OOAVO4Wp6t7bemyN9DMWIobhGjFNZSHmixtVJM4S7mzjkN2L5VBfG96Iy1i0'
        }
        """  # noqa:E501
        return ConsumerKeyRequest(self)

    def request_consumerkey(self, access_rules, redirect_url=None, allowedIPs=None):
        """
        Create a new "consumer key" identifying this application's end user. API
        will return a ``consumerKey`` and a ``validationUrl``. The end user must
        visit the ``validationUrl``, authenticate and validate the requested
        ``access_rules`` to link his account to the ``consumerKey``. Once this
        is done, he may optionally be redirected to ``redirect_url`` and the
        application can start using the ``consumerKey``. If adding an ``allowedIPs``
        parameter, the generated credentials will only be usable from these IPs.

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

            try:
                input = raw_input
            except NameError:
                pass

            # Request RO, /me API access
            access_rules = [
                {'method': 'GET', 'path': '/me'},
            ]

            # Request token
            validation = client.request_consumerkey(access_rules, redirect_url="https://optional-redirect-url.example.org", allowedIPs=["127.0.0.1/32"])

            print("Please visit", validation['validationUrl'], "to authenticate")
            input("and press Enter to continue...")

            # Print nice welcome message
            print("Welcome", client.get('/me')['firstname'])


        :param list access_rules: Mapping specifying requested privileges.
        :param str redirect_url: Where to redirect end user upon validation (optional).
        :param list allowedIPs: CIDRs that will be allowed to use these credentials (optional).
        :raises APIError: When ``self.call`` fails.
        :returns: dict with ``consumerKey`` and ``validationUrl`` keys
        :rtype: dict
        """  # noqa:E501
        res = self.post(
            "/auth/credential",
            _need_auth=False,
            accessRules=access_rules,
            redirection=redirect_url,
            allowedIPs=allowedIPs,
        )
        self._consumer_key = res["consumerKey"]
        return res

    # API shortcuts

    def _canonicalize_kwargs(self, kwargs):
        """
        If an API needs an argument colliding with a Python reserved keyword, it
        can be prefixed with an underscore. For example, ``from`` argument of
        ``POST /email/domain/{domain}/redirection`` may be replaced by ``_from``

        :param dict kwargs: input kwargs
        :return dict: filtered kawrgs
        """
        arguments = {}

        for k, v in kwargs.items():
            if k[0] == "_" and k[1:] in keyword.kwlist:
                k = k[1:]
            arguments[k] = v

        return arguments

    def _prepare_query_string(self, kwargs):
        """
        Boolean needs to be send as lowercase 'false' or 'true' in querystring.
        This function prepares arguments for querystring and encodes them.

        :param dict kwargs: input kwargs
        :return string: prepared querystring
        """
        arguments = {}

        for k, v in kwargs.items():
            if isinstance(v, bool):
                v = str(v).lower()
            elif v is None:
                v = "null"
            arguments[k] = v

        return urlencode(arguments)

    def get(self, _target, _need_auth=True, **kwargs):
        """
        'GET' :py:func:`Client.call` wrapper.

        Query string parameters can be set either directly in ``_target`` or as
        keyword arguments. If an argument collides with a Python reserved
        keyword, prefix it with a '_'. For instance, ``from`` becomes ``_from``.

        :param string _target: API method to call
        :param string _need_auth: If True, send authentication headers. This is
            the default
        """
        if kwargs:
            kwargs = self._canonicalize_kwargs(kwargs)
            query_string = self._prepare_query_string(kwargs)
            if query_string != "":
                if "?" in _target:
                    _target = "%s&%s" % (_target, query_string)
                else:
                    _target = "%s?%s" % (_target, query_string)

        return self.call("GET", _target, None, _need_auth)

    def put(self, _target, _need_auth=True, **kwargs):
        """
        'PUT' :py:func:`Client.call` wrapper

        Body parameters can be set either directly in ``_target`` or as keyword
        arguments. If an argument collides with a Python reserved keyword,
        prefix it with a '_'. For instance, ``from`` becomes ``_from``.

        :param string _target: API method to call
        :param string _need_auth: If True, send authentication headers. This is
            the default
        """
        kwargs = self._canonicalize_kwargs(kwargs)
        if not kwargs:
            kwargs = None
        return self.call("PUT", _target, kwargs, _need_auth)

    def post(self, _target, _need_auth=True, **kwargs):
        """
        'POST' :py:func:`Client.call` wrapper

        Body parameters can be set either directly in ``_target`` or as keyword
        arguments. If an argument collides with a Python reserved keyword,
        prefix it with a '_'. For instance, ``from`` becomes ``_from``.

        :param string _target: API method to call
        :param string _need_auth: If True, send authentication headers. This is
            the default
        """
        kwargs = self._canonicalize_kwargs(kwargs)
        if not kwargs:
            kwargs = None
        return self.call("POST", _target, kwargs, _need_auth)

    def delete(self, _target, _need_auth=True, **kwargs):
        """
        'DELETE' :py:func:`Client.call` wrapper

        Query string parameters can be set either directly in ``_target`` or as
        keyword arguments. If an argument collides with a Python reserved
        keyword, prefix it with a '_'. For instance, ``from`` becomes ``_from``.

        :param string _target: API method to call
        :param string _need_auth: If True, send authentication headers. This is
            the default
        """
        if kwargs:
            kwargs = self._canonicalize_kwargs(kwargs)
            query_string = self._prepare_query_string(kwargs)
            if query_string != "":
                if "?" in _target:
                    _target = "%s&%s" % (_target, query_string)
                else:
                    _target = "%s?%s" % (_target, query_string)

        return self.call("DELETE", _target, None, _need_auth)

    # low level helpers

    def call(self, method, path, data=None, need_auth=True):
        """
        Low level call helper. If ``consumer_key`` is not ``None``, inject
        authentication headers and sign the request.

        Request signature is a sha1 hash on following fields, joined by '+'
         - application_secret
         - consumer_key
         - METHOD
         - full request url
         - body
         - server current time (takes time delta into account)

        :param str method: HTTP verb. Usually one of GET, POST, PUT, DELETE
        :param str path: api entrypoint to call, relative to endpoint base path
        :param data: any json serializable data to send as request's body
        :param boolean need_auth: if False, bypass signature
        :raises HTTPError: when underlying request failed for network reason
        :raises InvalidResponse: when API response could not be decoded
        """
        # attempt request
        try:
            result = self.raw_call(method=method, path=path, data=data, need_auth=need_auth)
        except RequestException as error:
            raise HTTPError("Low HTTP request failed error", error)

        status = result.status_code

        # attempt to decode and return the response
        try:
            if status != 204:
                json_result = result.json()
            else:
                json_result = None
        except ValueError as error:
            raise InvalidResponse("Failed to decode API response", error)

        # error check
        if status >= 100 and status < 300:
            return json_result
        elif status == 403 and json_result.get("errorCode") == "NOT_GRANTED_CALL":
            raise NotGrantedCall(json_result.get("message"), response=result)
        elif status == 403 and json_result.get("errorCode") == "NOT_CREDENTIAL":
            raise NotCredential(json_result.get("message"), response=result)
        elif status == 403 and json_result.get("errorCode") == "INVALID_KEY":
            raise InvalidKey(json_result.get("message"), response=result)
        elif status == 403 and json_result.get("errorCode") == "INVALID_CREDENTIAL":
            raise InvalidCredential(json_result.get("message"), response=result)
        elif status == 403 and json_result.get("errorCode") == "FORBIDDEN":
            raise Forbidden(json_result.get("message"), response=result)
        elif status == 404:
            raise ResourceNotFoundError(json_result.get("message"), response=result)
        elif status == 400:
            raise BadParametersError(json_result.get("message"), response=result)
        elif status == 409:
            raise ResourceConflictError(json_result.get("message"), response=result)
        elif status == 460:
            raise ResourceExpiredError(json_result.get("message"), response=result)
        elif status == 0:
            raise NetworkError()
        else:
            raise APIError(json_result.get("message"), response=result)

    def _get_target(self, path):
        """
        _get_target returns the URL to target given an endpoint and a path.
        If the path starts with `/v1` or `/v2`, then remove the trailing `/1.0` from the endpoint.

        :param str path: path to use prefix from
        :returns: target with one of /1.0 and /v1|2 path segment
        :rtype: str
        """
        endpoint = self._endpoint
        if endpoint.endswith("/1.0") and path.startswith(("/v1", "/v2")):
            endpoint = endpoint[:-4]
        return endpoint + path

    def raw_call(self, method, path, data=None, need_auth=True, headers=None):
        """
        Lowest level call helper. If ``consumer_key`` is not ``None``, inject
        authentication headers and sign the request.
        Will return ``requests.Response`` object or let any
        ``requests`` exception pass through.

        Request signature is a sha1 hash on following fields, joined by '+'
         - application_secret
         - consumer_key
         - METHOD
         - full request url
         - body
         - server current time (takes time delta into account)

        :param str method: HTTP verb. Usually one of GET, POST, PUT, DELETE
        :param str path: api entrypoint to call, relative to endpoint base path
        :param data: any json serializable data to send as request's body
        :param boolean need_auth: if False, bypass signature
        :param dict headers: A dict containing the headers that should be sent to
                             the OVH API. ``raw_call`` will override the
                             OVH API authentication headers, as well as
                             the Content-Type header.
        """
        body = ""
        target = self._get_target(path)

        if headers is None:
            headers = {}

        # include payload
        if data is not None:
            headers["Content-type"] = "application/json"
            body = json.dumps(data, separators=(",", ":"))  # Separators to prevent adding useless spaces

        # sign request. Never sign 'time' or will recurse infinitely
        if need_auth:
            if self._oauth2:
                return self._oauth2.session.request(method, target, headers=headers, data=body, timeout=self._timeout)

            if not self._application_secret:
                raise InvalidKey("Invalid ApplicationSecret '%s'" % self._application_secret)

            if not self._consumer_key:
                raise InvalidKey("Invalid ConsumerKey '%s'" % self._consumer_key)

            now = str(int(time.time()) + self.time_delta)
            signature = hashlib.sha1()
            signature.update(
                "+".join([self._application_secret, self._consumer_key, method.upper(), target, body, now]).encode(
                    "utf-8"
                )
            )

            headers["X-Ovh-Consumer"] = self._consumer_key
            headers["X-Ovh-Timestamp"] = now
            headers["X-Ovh-Signature"] = "$1$" + signature.hexdigest()

        headers["X-Ovh-Application"] = self._application_key
        return self._session.request(method, target, headers=headers, data=body, timeout=self._timeout)
