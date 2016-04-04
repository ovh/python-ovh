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

from ovh import config
import unittest
import mock
import os

M_CONFIG_PATH = [
    './fixtures/etc_ovh.conf',
    './fixtures/home_ovh.conf',
    './fixtures/pwd_ovh.conf',
]

M_ENVIRON = {
    'OVH_ENDPOINT': 'endpoint from environ',
    'OVH_APPLICATION_KEY': 'application key from environ',
    'OVH_APPLICATION_SECRET': 'application secret from environ',
    'OVH_CONSUMER_KEY': 'consumer key from from environ',
}

class testConfig(unittest.TestCase):
    def setUp(self):
        """Overload configuration lookup path"""
        self._orig_CONFIG_PATH = config.CONFIG_PATH
        config.CONFIG_PATH = M_CONFIG_PATH

    def tearDown(self):
        """Restore configuraton lookup path"""
        config.CONFIG_PATH = self._orig_CONFIG_PATH

    def test_real_lookup_path(self):
        home = os.environ['HOME']
        pwd = os.environ['PWD']

        self.assertEqual([
           '/etc/ovh.conf',
           home+'/.ovh.conf',
           pwd+'/tests/ovh.conf',

        ], self._orig_CONFIG_PATH)

    def test_config_get_conf(self):
        conf = config.ConfigurationManager()

        self.assertEqual('runabove-ca', conf.get('default', 'endpoint'))
        self.assertEqual('This is a *fake* global application key',    conf.get('ovh-eu', 'application_key'))
        self.assertEqual('This is a *real* global application secret', conf.get('ovh-eu', 'application_secret'))
        self.assertEqual('I am kidding at home',                      conf.get('ovh-eu', 'consumer_key'))
        self.assertEqual('This is a fake local application key',   conf.get('runabove-ca', 'application_key'))
        self.assertEqual('This is a *real* local application key', conf.get('runabove-ca', 'application_secret'))
        self.assertEqual('I am locally kidding',                   conf.get('runabove-ca', 'consumer_key'))

        self.assertTrue(conf.get('ovh-eu', 'non-existent') is None)
        self.assertTrue(conf.get('ovh-ca', 'application_key') is None)
        self.assertTrue(conf.get('ovh-laponie', 'application_key') is None)

    def test_config_get_conf_env_rules_them_all(self):
        conf = config.ConfigurationManager()

        with mock.patch.dict('os.environ', M_ENVIRON):
            self.assertEqual(M_ENVIRON['OVH_ENDPOINT'],           conf.get('wathever', 'endpoint'))
            self.assertEqual(M_ENVIRON['OVH_APPLICATION_KEY'],    conf.get('wathever', 'application_key'))
            self.assertEqual(M_ENVIRON['OVH_APPLICATION_SECRET'], conf.get('wathever', 'application_secret'))
            self.assertEqual(M_ENVIRON['OVH_CONSUMER_KEY'],       conf.get('wathever', 'consumer_key'))

        self.assertTrue(conf.get('ovh-eu', 'non-existent') is None)
