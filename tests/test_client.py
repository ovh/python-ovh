# -*- encoding: utf-8 -*-
#
# Copyright (c) 2013-2018, OVH SAS.
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
# THIS SOFTWARE IS PROVIDED BY OVH SAS AND CONTRIBUTORS ``AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL OVH SAS AND CONTRIBUTORS BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import unittest
import mock
import json

from ovh.vendor import requests

try:
    from collections import OrderedDict
except ImportError:
    # Python 2.6
    from ordereddict import OrderedDict

from ovh.client import Client, ENDPOINTS
from ovh.exceptions import (
    APIError, NetworkError, InvalidResponse, InvalidRegion, ReadOnlyError,
    ResourceNotFoundError, BadParametersError, ResourceConflictError, HTTPError,
    InvalidKey, InvalidCredential, NotGrantedCall, NotCredential, Forbidden,
    ResourceExpiredError,
)

M_ENVIRON = {
    'OVH_ENDPOINT': 'soyoustart-ca',
    'OVH_APPLICATION_KEY': 'application key from environ',
    'OVH_APPLICATION_SECRET': 'application secret from environ',
    'OVH_CONSUMER_KEY': 'consumer key from from environ',
}

M_CUSTOM_CONFIG_PATH = './fixtures/custom_ovh.conf'

APPLICATION_KEY = 'fake application key'
APPLICATION_SECRET = 'fake application secret'
CONSUMER_KEY = 'fake consumer key'
ENDPOINT = 'ovh-eu'
ENDPOINT_BAD = 'laponie'
BASE_URL = 'https://eu.api.ovh.com/1.0'
FAKE_URL = 'http://gopher.ovh.net/'
FAKE_TIME = 1404395889.467238

FAKE_METHOD = 'MeThOd'
FAKE_PATH = '/unit/test'
FAKE_PATH_BATCH = '/unit/test/1,2'

TIMEOUT = 180

class testClient(unittest.TestCase):
    def setUp(self):
        self.time_patch = mock.patch('time.time', return_value=FAKE_TIME)
        self.time_patch.start()

    def tearDown(self):
        self.time_patch.stop()

    ## test helpers

    def test_init(self):
        # nominal
        api = Client(ENDPOINT, APPLICATION_KEY, APPLICATION_SECRET, CONSUMER_KEY)
        self.assertEqual(APPLICATION_KEY, api._application_key)
        self.assertEqual(APPLICATION_SECRET, api._application_secret)
        self.assertEqual(CONSUMER_KEY, api._consumer_key)
        self.assertTrue(api._time_delta is None)
        self.assertEqual(TIMEOUT, api._timeout)

        # override default timeout
        timeout = (1, 1)
        api = Client(ENDPOINT, APPLICATION_KEY, APPLICATION_SECRET,
                     CONSUMER_KEY, timeout=timeout)
        self.assertEqual(timeout, api._timeout)

        # invalid region
        self.assertRaises(InvalidRegion, Client, ENDPOINT_BAD, '', '', '')

    def test_init_from_config(self):
        with mock.patch.dict('os.environ', M_ENVIRON):
            api = Client()

        self.assertEqual('https://ca.api.soyoustart.com/1.0',      api._endpoint)
        self.assertEqual(M_ENVIRON['OVH_APPLICATION_KEY'],    api._application_key)
        self.assertEqual(M_ENVIRON['OVH_APPLICATION_SECRET'], api._application_secret)
        self.assertEqual(M_ENVIRON['OVH_CONSUMER_KEY'],       api._consumer_key)

    def test_init_from_custom_config(self):
        # custom config file
        api = Client(config_file=M_CUSTOM_CONFIG_PATH)

        self.assertEqual('https://ca.api.ovh.com/1.0', api._endpoint)
        self.assertEqual('This is a fake custom application key', api._application_key)
        self.assertEqual('This is a *real* custom application key', api._application_secret)
        self.assertEqual('I am customingly kidding', api._consumer_key)

    @mock.patch.object(Client, 'call')
    def test_time_delta(self, m_call):
        api = Client(ENDPOINT, APPLICATION_KEY, APPLICATION_SECRET, CONSUMER_KEY)
        m_call.return_value = 1404395895
        api._time_delta = None

        # nominal
        time_delta = api.time_delta
        m_call.assert_called_once_with('GET', '/auth/time', None, False, None)
        self.assertEqual(time_delta, 6)
        self.assertEqual(api._time_delta, 6)

        # ensure cache
        m_call.return_value = 0
        m_call.reset_mock()
        self.assertEqual(api.time_delta, 6)
        self.assertFalse(m_call.called)

    @mock.patch.object(Client, 'call')
    def test_request_consumerkey(self, m_call):
        api = Client(ENDPOINT, APPLICATION_KEY, APPLICATION_SECRET, CONSUMER_KEY)

        # nominal
        FAKE_RULES = object()
        FAKE_CK = object()
        RET = {'consumerKey': FAKE_CK}
        m_call.return_value = RET

        ret = api.request_consumerkey(FAKE_RULES, FAKE_URL)

        self.assertEqual(RET, ret)
        m_call.assert_called_once_with('POST', '/auth/credential', {
            'redirection': FAKE_URL,
            'accessRules': FAKE_RULES,
        }, False)

    def test_new_consumer_key_request(self):
        api = Client(ENDPOINT, APPLICATION_KEY, APPLICATION_SECRET, CONSUMER_KEY)

        ck = api.new_consumer_key_request()
        self.assertEqual(ck._client, api)

    ## test wrappers

    def test__canonicalize_kwargs(self):
        api = Client(ENDPOINT, APPLICATION_KEY, APPLICATION_SECRET, CONSUMER_KEY)

        self.assertEqual({}, api._canonicalize_kwargs({}))
        self.assertEqual({'from': 'value'}, api._canonicalize_kwargs({'from': 'value'}))
        self.assertEqual({'_to': 'value'}, api._canonicalize_kwargs({'_to': 'value'}))
        self.assertEqual({'from': 'value'}, api._canonicalize_kwargs({'_from': 'value'}))

    @mock.patch.object(Client, 'call')
    def test_get(self, m_call):
        # basic test
        api = Client(ENDPOINT, APPLICATION_KEY, APPLICATION_SECRET, CONSUMER_KEY)
        self.assertEqual(m_call.return_value, api.get(FAKE_URL))
        m_call.assert_called_once_with('GET', FAKE_URL, None, True, None)

        # append query string
        m_call.reset_mock()
        api = Client(ENDPOINT, APPLICATION_KEY, APPLICATION_SECRET, CONSUMER_KEY)
        self.assertEqual(m_call.return_value, api.get(FAKE_URL, param="test"))
        m_call.assert_called_once_with('GET', FAKE_URL+'?param=test', None, True, None)

        # append to existing query string
        m_call.reset_mock()
        api = Client(ENDPOINT, APPLICATION_KEY, APPLICATION_SECRET, CONSUMER_KEY)
        self.assertEqual(m_call.return_value, api.get(FAKE_URL+'?query=string', param="test"))
        m_call.assert_called_once_with('GET', FAKE_URL+'?query=string&param=test', None, True, None)

        # boolean arguments
        m_call.reset_mock()
        api = Client(ENDPOINT, APPLICATION_KEY, APPLICATION_SECRET, CONSUMER_KEY)
        self.assertEqual(m_call.return_value, api.get(FAKE_URL+'?query=string', checkbox=True))
        m_call.assert_called_once_with('GET', FAKE_URL+'?query=string&checkbox=true', None, True, None)

        # keyword calling convention
        m_call.reset_mock()
        api = Client(ENDPOINT, APPLICATION_KEY, APPLICATION_SECRET, CONSUMER_KEY)
        self.assertEqual(m_call.return_value, api.get(FAKE_URL, _from="start", to="end"))
        try:
            m_call.assert_called_once_with('GET', FAKE_URL+'?to=end&from=start', None, True, None)
        except:
            m_call.assert_called_once_with('GET', FAKE_URL+'?from=start&to=end', None, True, None)

        # batch call
        m_call.reset_mock()
        api = Client(ENDPOINT, APPLICATION_KEY, APPLICATION_SECRET, CONSUMER_KEY)
        self.assertEqual(m_call.return_value, api.get(FAKE_URL, _batch=','))
        m_call.assert_called_once_with('GET', FAKE_URL, None, True, ',')


    @mock.patch.object(Client, 'call')
    def test_delete(self, m_call):
        api = Client(ENDPOINT, APPLICATION_KEY, APPLICATION_SECRET, CONSUMER_KEY)
        self.assertEqual(m_call.return_value, api.delete(FAKE_URL))
        m_call.assert_called_once_with('DELETE', FAKE_URL, None, True)

    @mock.patch.object(Client, 'call')
    def test_post(self, m_call):
        PAYLOAD = {
            'arg1': object(),
            'arg2': object(),
            'arg3': object(),
            'arg4': False,
        }

        api = Client(ENDPOINT, APPLICATION_KEY, APPLICATION_SECRET, CONSUMER_KEY)
        self.assertEqual(m_call.return_value, api.post(FAKE_URL, **PAYLOAD))
        m_call.assert_called_once_with('POST', FAKE_URL, PAYLOAD, True)

    @mock.patch.object(Client, 'call')
    def test_put(self, m_call):
        PAYLOAD = {
            'arg1': object(),
            'arg2': object(),
            'arg3': object(),
            'arg4': False,
        }

        api = Client(ENDPOINT, APPLICATION_KEY, APPLICATION_SECRET, CONSUMER_KEY)
        self.assertEqual(m_call.return_value, api.put(FAKE_URL, **PAYLOAD))
        m_call.assert_called_once_with('PUT', FAKE_URL, PAYLOAD, True)

    ## test core function

    @mock.patch('ovh.client.Session.request')
    def test_call_no_sign(self, m_req):
        m_res = m_req.return_value
        m_json = m_res.json.return_value

        api = Client(ENDPOINT, APPLICATION_KEY, APPLICATION_SECRET)

        # nominal
        m_res.status_code = 200
        self.assertEqual(m_json, api.call(FAKE_METHOD, FAKE_PATH, None, False))
        m_req.assert_called_once_with(
            FAKE_METHOD, BASE_URL+'/unit/test',
            headers={'X-Ovh-Application': APPLICATION_KEY}, data='',
            timeout=TIMEOUT
        )
        m_req.reset_mock()

        # data, nominal
        m_res.status_code = 200
        data = {'key': 'value'}
        j_data = json.dumps(data)
        self.assertEqual(m_json, api.call(FAKE_METHOD, FAKE_PATH, data, False))
        m_req.assert_called_once_with(
            FAKE_METHOD, BASE_URL+'/unit/test',
            headers={
                'X-Ovh-Application': APPLICATION_KEY,
                'Content-type': 'application/json',
            }, data=j_data, timeout=TIMEOUT
        )
        m_req.reset_mock()

        # request fails, somehow
        m_req.side_effect = requests.RequestException
        self.assertRaises(HTTPError, api.call, FAKE_METHOD, FAKE_PATH, None, False)
        m_req.side_effect = None

        # response decoding fails
        m_res.json.side_effect = ValueError
        self.assertRaises(InvalidResponse, api.call, FAKE_METHOD, FAKE_PATH, None, False)
        m_res.json.side_effect = None

        # HTTP errors
        m_res.status_code = 404
        self.assertRaises(ResourceNotFoundError, api.call, FAKE_METHOD, FAKE_PATH, None, False)
        m_res.status_code = 403
        m_res.json.return_value = {'errorCode': "NOT_GRANTED_CALL"}
        self.assertRaises(NotGrantedCall, api.call, FAKE_METHOD, FAKE_PATH, None, False)
        m_res.status_code = 403
        m_res.json.return_value = {'errorCode': "NOT_CREDENTIAL"}
        self.assertRaises(NotCredential, api.call, FAKE_METHOD, FAKE_PATH, None, False)
        m_res.status_code = 403
        m_res.json.return_value = {'errorCode': "INVALID_KEY"}
        self.assertRaises(InvalidKey, api.call, FAKE_METHOD, FAKE_PATH, None, False)
        m_res.status_code = 403
        m_res.json.return_value = {'errorCode': "INVALID_CREDENTIAL"}
        self.assertRaises(InvalidCredential, api.call, FAKE_METHOD, FAKE_PATH, None, False)
        m_res.status_code = 403
        m_res.json.return_value = {'errorCode': "FORBIDDEN"}
        self.assertRaises(Forbidden, api.call, FAKE_METHOD, FAKE_PATH, None, False)
        m_res.status_code = 400
        self.assertRaises(BadParametersError, api.call, FAKE_METHOD, FAKE_PATH, None, False)
        m_res.status_code = 409
        self.assertRaises(ResourceConflictError, api.call, FAKE_METHOD, FAKE_PATH, None, False)
        m_res.status_code = 460
        self.assertRaises(ResourceExpiredError, api.call, FAKE_METHOD, FAKE_PATH, None, False)
        m_res.status_code = 0
        self.assertRaises(NetworkError, api.call, FAKE_METHOD, FAKE_PATH, None, False)
        m_res.status_code = 99
        self.assertRaises(APIError, api.call, FAKE_METHOD, FAKE_PATH, None, False)
        m_res.status_code = 306
        self.assertRaises(APIError, api.call, FAKE_METHOD, FAKE_PATH, None, False)


    @mock.patch('ovh.client.Session.request')
    def test_call_query_id(self, m_req):
        m_res = m_req.return_value
        m_json = m_res.json.return_value
        m_res.headers = {"X-OVH-QUERYID": "FR.test1"}

        api = Client(ENDPOINT, APPLICATION_KEY, APPLICATION_SECRET)

        m_res.status_code = 99
        self.assertRaises(APIError, api.call, FAKE_METHOD, FAKE_PATH, None, False)
        try:
            api.call(FAKE_METHOD, FAKE_PATH, None, False)
            self.assertEqual(0, 1)   # should fail as method have to raise APIError
        except APIError as e:
            self.assertEqual(e.query_id, "FR.test1")


    @mock.patch('ovh.client.Session.request')
    @mock.patch('ovh.client.Client.time_delta', new_callable=mock.PropertyMock)
    def test_call_signature(self, m_time_delta, m_req):
        m_res = m_req.return_value
        m_json = m_res.json.return_value
        m_time_delta.return_value = 42

        api = Client(ENDPOINT, APPLICATION_KEY, APPLICATION_SECRET, CONSUMER_KEY)

        # nominal
        m_res.status_code = 200
        self.assertEqual(m_json, api.call(FAKE_METHOD, FAKE_PATH, None, True))
        m_time_delta.assert_called_once_with()
        m_req.assert_called_once_with(
            FAKE_METHOD, BASE_URL+'/unit/test',
            headers={
                'X-Ovh-Consumer': CONSUMER_KEY,
                'X-Ovh-Application': APPLICATION_KEY,
                'X-Ovh-Signature': '$1$16ae5ba8c63841b1951575be905867991d5f49dc',
                'X-Ovh-Timestamp': '1404395931',
            }, data='', timeout=TIMEOUT
        )
        m_time_delta.reset_mock()
        m_req.reset_mock()


        # data, nominal
        data = OrderedDict([('some', 'random'), ('data', 42)])
        m_res.status_code = 200
        self.assertEqual(m_json, api.call(FAKE_METHOD, FAKE_PATH, data, True))
        m_time_delta.assert_called_once_with()
        m_req.assert_called_once_with(
            FAKE_METHOD, BASE_URL+'/unit/test',
            headers={
                'X-Ovh-Consumer': CONSUMER_KEY,
                'X-Ovh-Application': APPLICATION_KEY,
                'Content-type': 'application/json',
                'X-Ovh-Timestamp': '1404395931',
                'X-Ovh-Signature': '$1$9acb1ac0120006d16261a635aed788e83ab172d2',
                }, data=json.dumps(data), timeout=TIMEOUT
        )
        m_time_delta.reset_mock()
        m_req.reset_mock()

        # Overwrite configuration to avoid interfering with any local config
        from ovh.client import config
        try:
            from ConfigParser import RawConfigParser
        except ImportError:
            # Python 3
            from configparser import RawConfigParser

        self._orig_config = config.config
        config.config = RawConfigParser()

        # errors
        try:
            api = Client(ENDPOINT, APPLICATION_KEY, None, CONSUMER_KEY)
            self.assertRaises(InvalidKey, api.call, FAKE_METHOD, FAKE_PATH, None, True)
            api = Client(ENDPOINT, APPLICATION_KEY, APPLICATION_SECRET, None)
            self.assertRaises(InvalidKey, api.call, FAKE_METHOD, FAKE_PATH, None, True)
        finally:
            # Restore configuration
            config.config = self._orig_config

    @mock.patch('ovh.client.Session.request', return_value="Let's assume requests will return this")
    def test_raw_call(self, m_req):
        api = Client(ENDPOINT, APPLICATION_KEY, APPLICATION_SECRET)
        r = api.raw_call(FAKE_METHOD, FAKE_PATH, None, False)
        self.assertEqual(r, "Let's assume requests will return this")

    @mock.patch('ovh.client.Session.request', return_value=["first item", "second item"])
    def test_raw_call_batch(self, m_req):
        api = Client(ENDPOINT, APPLICATION_KEY, APPLICATION_SECRET)
        r = api.raw_call(FAKE_METHOD, FAKE_PATH_BATCH, None, False, ',')
        self.assertEqual(r, ["first item", "second item"])

    # Perform real API tests.
    def test_endpoints(self):
        for endpoint in ENDPOINTS.keys():
            auth_time = Client(endpoint).get('/auth/time', _need_auth=False)
            self.assertTrue(auth_time > 0)

