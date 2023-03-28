# Copyright (c) 2013-2023, OVH SAS.
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

from unittest import mock

import pytest
import requests

from ovh.client import ENDPOINTS, Client
from ovh.exceptions import (
    APIError,
    BadParametersError,
    Forbidden,
    HTTPError,
    InvalidCredential,
    InvalidKey,
    InvalidResponse,
    NetworkError,
    NotCredential,
    NotGrantedCall,
    ResourceConflictError,
    ResourceExpiredError,
    ResourceNotFoundError,
)

# Mock values
MockApplicationKey = "TDPKJdwZwAQPwKX2"
MockApplicationSecret = "9ufkBmLaTQ9nz5yMUlg79taH0GNnzDjk"
MockConsumerKey = "5mBuy6SUQcRw2ZUxg0cG68BoDKpED4KY"
MockTime = 1457018875


class TestClient:
    @mock.patch("time.time", return_value=1457018875.467238)
    @mock.patch.object(Client, "call", return_value=1457018881)
    def test_time_delta(self, m_call, m_time):
        api = Client("ovh-eu")
        assert api._time_delta is None
        assert m_call.called is False
        assert m_time.called is False

        # nominal
        assert api.time_delta == 6
        assert m_call.called is True
        assert m_time.called is True
        assert api._time_delta == 6
        assert m_call.call_args_list == [mock.call("GET", "/auth/time", None, False)]

        # ensure cache
        m_call.reset_mock()
        assert api.time_delta == 6
        assert m_call.called is False

    @mock.patch.object(Client, "call", return_value={"consumerKey": "CK"})
    def test_request_consumerkey(self, m_call):
        api = Client("ovh-eu")
        ret = api.request_consumerkey([{"method": "GET", "path": "/"}], "https://example.com")

        m_call.assert_called_once_with(
            "POST",
            "/auth/credential",
            {
                "redirection": "https://example.com",
                "accessRules": [{"method": "GET", "path": "/"}],
            },
            False,
        )
        assert ret == {"consumerKey": "CK"}

    def test_new_consumer_key_request(self):
        api = Client("ovh-eu")
        ck = api.new_consumer_key_request()
        assert ck._client == api

    # test wrappers

    def test__canonicalize_kwargs(self):
        api = Client("ovh-eu")
        assert api._canonicalize_kwargs({}) == {}
        assert api._canonicalize_kwargs({"from": "value"}) == {"from": "value"}
        assert api._canonicalize_kwargs({"_to": "value"}) == {"_to": "value"}
        assert api._canonicalize_kwargs({"_from": "value"}) == {"from": "value"}

    @mock.patch.object(Client, "call")
    def test_query_string(self, m_call):
        api = Client("ovh-eu")

        for method, call in (("GET", api.get), ("DELETE", api.delete)):
            m_call.reset_mock()

            assert call("https://eu.api.ovh.com/") == m_call.return_value
            assert call("https://eu.api.ovh.com/", param="test") == m_call.return_value
            assert call("https://eu.api.ovh.com/?query=string", param="test") == m_call.return_value
            assert call("https://eu.api.ovh.com/?query=string", checkbox=True) == m_call.return_value
            assert call("https://eu.api.ovh.com/", _from="start", to="end") == m_call.return_value

            assert m_call.call_args_list == [
                mock.call(method, "https://eu.api.ovh.com/", None, True),
                mock.call(method, "https://eu.api.ovh.com/?param=test", None, True),
                mock.call(method, "https://eu.api.ovh.com/?query=string&param=test", None, True),
                mock.call(method, "https://eu.api.ovh.com/?query=string&checkbox=true", None, True),
                mock.call(method, "https://eu.api.ovh.com/?from=start&to=end", None, True),
            ]

    @mock.patch.object(Client, "call")
    def test_body(self, m_call):
        api = Client("ovh-eu")

        for method, call in (("POST", api.post), ("PUT", api.put)):
            m_call.reset_mock()

            assert call("https://eu.api.ovh.com/") == m_call.return_value
            assert call("https://eu.api.ovh.com/", param="test") == m_call.return_value
            assert call("https://eu.api.ovh.com/?query=string", param="test") == m_call.return_value
            assert call("https://eu.api.ovh.com/?query=string", checkbox=True) == m_call.return_value
            assert call("https://eu.api.ovh.com/", _from="start", to="end") == m_call.return_value

            assert m_call.call_args_list == [
                mock.call(method, "https://eu.api.ovh.com/", None, True),
                mock.call(method, "https://eu.api.ovh.com/", {"param": "test"}, True),
                mock.call(method, "https://eu.api.ovh.com/?query=string", {"param": "test"}, True),
                mock.call(method, "https://eu.api.ovh.com/?query=string", {"checkbox": True}, True),
                mock.call(method, "https://eu.api.ovh.com/", {"from": "start", "to": "end"}, True),
            ]

    # test core function

    @mock.patch("time.time", return_value=1457018875.467238)
    @mock.patch("ovh.client.Session.request")
    @mock.patch("ovh.client.Client.time_delta", new_callable=mock.PropertyMock, return_value=0)
    def test_call_signature(self, m_time_delta, m_req, m_time):
        m_res = m_req.return_value
        m_res.status_code = 200
        m_json = m_res.json.return_value

        body = {"a": "b", "c": "d"}
        j_body = '{"a":"b","c":"d"}'

        api = Client("ovh-eu", MockApplicationKey, MockApplicationSecret, MockConsumerKey)
        urlUnauth = "https://eu.api.ovh.com/1.0/unauth"
        urlAuth = "https://eu.api.ovh.com/1.0/auth"

        for method in "GET", "POST", "PUT", "DELETE":
            assert api.call(method, "/unauth", None if method in ("GET", "DELETE") else body, False) == m_json
            assert api.call(method, "/auth", None if method in ("GET", "DELETE") else body, True) == m_json

        signatures = {
            "GET": "$1$e9556054b6309771395efa467c22e627407461ad",
            "POST": "$1$ec2fb5c7a81f64723c77d2e5b609ae6f58a84fc1",
            "PUT": "$1$8a75a9e7c8e7296c9dbeda6a2a735eb6bd58ec4b",
            "DELETE": "$1$a1eecd00b3b02b6cf5708b84b9ff42059a950d85",
        }

        def _h(m, auth):
            h = {"X-Ovh-Application": MockApplicationKey}
            if m in ("POST", "PUT"):
                h["Content-type"] = "application/json"
            if auth:
                h["X-Ovh-Consumer"] = MockConsumerKey
                h["X-Ovh-Timestamp"] = str(MockTime)
                h["X-Ovh-Signature"] = signatures[m]
            return h

        assert m_req.call_args_list == [
            mock.call("GET", urlUnauth, headers=_h("GET", False), data="", timeout=180),
            mock.call("GET", urlAuth, headers=_h("GET", True), data="", timeout=180),
            mock.call("POST", urlUnauth, headers=_h("POST", False), data=j_body, timeout=180),
            mock.call("POST", urlAuth, headers=_h("POST", True), data=j_body, timeout=180),
            mock.call("PUT", urlUnauth, headers=_h("PUT", False), data=j_body, timeout=180),
            mock.call("PUT", urlAuth, headers=_h("PUT", True), data=j_body, timeout=180),
            mock.call("DELETE", urlUnauth, headers=_h("DELETE", False), data="", timeout=180),
            mock.call("DELETE", urlAuth, headers=_h("DELETE", True), data="", timeout=180),
        ]

    @mock.patch("ovh.client.Session.request")
    def test_call_query_id(self, m_req):
        m_res = m_req.return_value
        m_res.status_code = 99
        m_res.headers = {"X-OVH-QUERYID": "FR.test1"}

        api = Client("ovh-eu", application_key=MockApplicationKey)
        with pytest.raises(APIError) as e:
            api.call("GET", "/unit/test", None, False)
        assert e.value.query_id == "FR.test1"

    @mock.patch("ovh.client.Session.request")
    def test_call_errors(self, m_req):
        m_res = m_req.return_value

        api = Client("ovh-eu", application_key=MockApplicationKey)

        # request fails, somehow
        m_req.side_effect = requests.RequestException
        with pytest.raises(HTTPError):
            api.call("GET", "/unauth", None, False)
        m_req.side_effect = None

        # response decoding fails
        m_res.json.side_effect = ValueError
        with pytest.raises(InvalidResponse):
            api.call("GET", "/unauth", None, False)
        m_res.json.side_effect = None

        # HTTP errors
        for status_code, body, exception in (
            (404, {}, ResourceNotFoundError),
            (403, {"errorCode": "NOT_GRANTED_CALL"}, NotGrantedCall),
            (403, {"errorCode": "NOT_CREDENTIAL"}, NotCredential),
            (403, {"errorCode": "INVALID_KEY"}, InvalidKey),
            (403, {"errorCode": "INVALID_CREDENTIAL"}, InvalidCredential),
            (403, {"errorCode": "FORBIDDEN"}, Forbidden),
            (400, {}, BadParametersError),
            (409, {}, ResourceConflictError),
            (460, {}, ResourceExpiredError),
            (0, {}, NetworkError),
            (99, {}, APIError),
            (306, {}, APIError),
        ):
            m_res.status_code = status_code
            m_res.json.return_value = body
            with pytest.raises(exception):
                api.call("GET", "/unauth", None, False)

        # errors
        api = Client("ovh-eu", MockApplicationKey, None, MockConsumerKey)
        with pytest.raises(InvalidKey):
            api.call("GET", "/unit/test", None, True)
        api = Client("ovh-eu", MockApplicationKey, MockApplicationSecret, None)
        with pytest.raises(InvalidKey):
            api.call("GET", "/unit/test", None, True)

    @mock.patch("ovh.client.Session.request", return_value="Let's assume requests will return this")
    def test_raw_call_with_headers(self, m_req):
        api = Client("ovh-eu", MockApplicationKey)
        r = api.raw_call("GET", "/unit/path", None, False, headers={"Custom-Header": "1"})
        assert r == "Let's assume requests will return this"
        assert m_req.call_args_list == [
            mock.call(
                "GET",
                "https://eu.api.ovh.com/1.0/unit/path",
                headers={
                    "Custom-Header": "1",
                    "X-Ovh-Application": MockApplicationKey,
                },
                data="",
                timeout=180,
            )
        ]

    # Perform real API tests.
    def test_endpoints(self):
        for endpoint in ENDPOINTS.keys():
            auth_time = Client(endpoint).get("/auth/time", _need_auth=False)
            assert auth_time > 0

    @mock.patch("time.time", return_value=1457018875.467238)
    @mock.patch("ovh.client.Session.request")
    @mock.patch("ovh.client.Client.time_delta", new_callable=mock.PropertyMock, return_value=0)
    def test_version_in_url(self, m_time_delta, m_req, m_time):
        m_res = m_req.return_value
        m_res.status_code = 200

        api = Client("ovh-eu", MockApplicationKey, MockApplicationSecret, MockConsumerKey)
        api.call("GET", "/call", None, True)
        api.call("GET", "/v1/call", None, True)
        api.call("GET", "/v2/call", None, True)

        signatures = {
            "1.0": "$1$7f2db49253edfc41891023fcd1a54cf61db05fbb",
            "v1": "$1$e6e7906d385eb28adcbfbe6b66c1528a42d741ad",
            "v2": "$1$bb63b132a6f84ad5433d0c534d48d3f7c3804285",
        }

        def _h(prefix):
            return {
                "X-Ovh-Application": MockApplicationKey,
                "X-Ovh-Consumer": MockConsumerKey,
                "X-Ovh-Timestamp": str(MockTime),
                "X-Ovh-Signature": signatures[prefix],
            }

        assert m_req.call_args_list == [
            mock.call("GET", "https://eu.api.ovh.com/1.0/call", headers=_h("1.0"), data="", timeout=180),
            mock.call("GET", "https://eu.api.ovh.com/v1/call", headers=_h("v1"), data="", timeout=180),
            mock.call("GET", "https://eu.api.ovh.com/v2/call", headers=_h("v2"), data="", timeout=180),
        ]
