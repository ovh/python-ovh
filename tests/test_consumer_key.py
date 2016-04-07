# -*- encoding: utf-8 -*-
#
# Copyright (c) 2013-2016, OVH SAS.
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
import requests
import mock

class testConsumerKeyRequest(unittest.TestCase):
    def test_add_rules(self):
        # Prepare
        import ovh
        m_client = mock.Mock()
        ck = ovh.ConsumerKeyRequest(m_client)

        # Test: No-op
        self.assertEqual([], ck._access_rules)
        ck._access_rules = []

        # Test: allow one
        ck.add_rule("GET", '/me')
        self.assertEqual([
            {'method': 'GET', 'path': '/me'},
        ], ck._access_rules)
        ck._access_rules = []

        # Test: allow safe methods on domain
        ck.add_rules(ovh.API_READ_WRITE_SAFE, '/domains/test.com')
        self.assertEqual([
            {'method': 'GET',  'path': '/domains/test.com'},
            {'method': 'POST', 'path': '/domains/test.com'},
            {'method': 'PUT',  'path': '/domains/test.com'},
        ], ck._access_rules)
        ck._access_rules = []

        # Test: allow all sms, strips suffix
        ck.add_recursive_rules(ovh.API_READ_WRITE, '/sms/*')
        self.assertEqual([
            {'method': 'GET',    'path': '/sms'},
            {'method': 'POST',   'path': '/sms'},
            {'method': 'PUT',    'path': '/sms'},
            {'method': 'DELETE', 'path': '/sms'},

            {'method': 'GET',    'path': '/sms/*'},
            {'method': 'POST',   'path': '/sms/*'},
            {'method': 'PUT',    'path': '/sms/*'},
            {'method': 'DELETE', 'path': '/sms/*'},
        ], ck._access_rules)
        ck._access_rules = []

        # Test: allow all, does not insert the empty rule
        ck.add_recursive_rules(ovh.API_READ_WRITE, '/')
        self.assertEqual([
            {'method': 'GET',    'path': '/*'},
            {'method': 'POST',   'path': '/*'},
            {'method': 'PUT',    'path': '/*'},
            {'method': 'DELETE', 'path': '/*'},
        ], ck._access_rules)
        ck._access_rules = []

        # Test launch request
        ck.add_recursive_rules(ovh.API_READ_WRITE, '/')
        self.assertEqual(m_client.request_consumerkey.return_value, ck.request())
        m_client.request_consumerkey.assert_called_once_with(ck._access_rules, None)

