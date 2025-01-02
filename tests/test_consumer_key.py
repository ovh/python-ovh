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

import ovh


class TestConsumerKey:
    def test_add_rules(self):
        # Prepare
        m_client = mock.Mock()
        ck = ovh.ConsumerKeyRequest(m_client)

        # Test: No-op
        assert ck._access_rules == []

        # Test: allow one
        ck.add_rule("GET", "/me")
        assert ck._access_rules == [{"method": "GET", "path": "/me"}]

        # Test: allow RO on /xdsl
        ck._access_rules = []
        ck.add_rules(ovh.API_READ_ONLY, "/xdsl")
        assert ck._access_rules == [
            {"method": "GET", "path": "/xdsl"},
        ]

        # Test: allow safe methods on domain
        ck._access_rules = []
        ck.add_rules(ovh.API_READ_WRITE_SAFE, "/domains/test.com")
        assert ck._access_rules == [
            {"method": "GET", "path": "/domains/test.com"},
            {"method": "POST", "path": "/domains/test.com"},
            {"method": "PUT", "path": "/domains/test.com"},
        ]

        # Test: allow all sms, strips suffix
        ck._access_rules = []
        ck.add_recursive_rules(ovh.API_READ_WRITE, "/sms/*")
        assert ck._access_rules == [
            {"method": "GET", "path": "/sms"},
            {"method": "POST", "path": "/sms"},
            {"method": "PUT", "path": "/sms"},
            {"method": "DELETE", "path": "/sms"},
            {"method": "GET", "path": "/sms/*"},
            {"method": "POST", "path": "/sms/*"},
            {"method": "PUT", "path": "/sms/*"},
            {"method": "DELETE", "path": "/sms/*"},
        ]

        # Test: allow all, does not insert the empty rule
        ck._access_rules = []
        ck.add_recursive_rules(ovh.API_READ_WRITE, "/")
        assert ck._access_rules == [
            {"method": "GET", "path": "/*"},
            {"method": "POST", "path": "/*"},
            {"method": "PUT", "path": "/*"},
            {"method": "DELETE", "path": "/*"},
        ]

        # Test launch request
        ck._access_rules = []
        ck.add_recursive_rules(ovh.API_READ_WRITE, "/")
        assert ck.request() is m_client.request_consumerkey.return_value
        m_client.request_consumerkey.assert_called_once_with(ck._access_rules, None, None)
