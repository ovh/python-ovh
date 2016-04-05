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
This module provides a consumer key creation helper. Consumer keys are linked
with permissions defining whicg endpoint they are allowed to call. Just like
a physical key can unlock some doors but not others.

OVH API consumer keys authorization is pattern based. This makes it extremely
powerful and flexible as it may apply on only a very specific subset of the API
but it's also trickier to get right on simple scenarios.

Hence this module
"""

# Common authorization patterns
API_READ_ONLY       = ["GET"]
API_READ_WRITE      = ["GET", "POST", "PUT", "DELETE"]
API_READ_WRITE_SAFE = ["GET", "POST", "PUT"]

class ConsumerKeyRequest(object):
    '''
    ConsumerKey request. The generated consumer key will be linked to the
    client's ``application_key``. When performing the request, the
    ``consumer_key`` will automatically be registered in the client.

    It is recommended to save the generated key as soon as it validated to avoid
    requesting a new one on each API access.
    '''

    def __init__(self, client):
        '''
        Create a new consumer key helper on API ``client``. The keys will be
        tied to the ``application_key`` defined in the client.
        '''
        self._client = client
        self._access_rules = []

    def request(self, redirect_url=None):
        '''
        Create the consumer key with the configures autorizations. The user will
        need to validate it befor it can be used with the API

        >>> ck.request()
        {
            'state': 'pendingValidation',
            'consumerKey': 'TnpZAd5pYNqxk4RhlPiSRfJ4WrkmII2i',
            'validationUrl': 'https://eu.api.ovh.com/auth/?credentialToken=now2OOAVO4Wp6t7bemyN9DMWIobhGjFNZSHmixtVJM4S7mzjkN2L5VBfG96Iy1i0'
        }
        '''
        return self._client.request_consumerkey(self._access_rules, redirect_url)

    def add_rule(self, method, path):
        '''
        Add a new rule to the request. Will grant the ``(method, path)`` tuple.
        Path can be any API route pattern like ``/sms/*`` or ``/me``. For example,
        to grant RO access on personal data:

        >>> ck.add_rule("GET", "/me")
        '''
        self._access_rules.append({'method': method.upper(), 'path': path})

    def add_rules(self, methods, path):
        '''
        Add rules for ``path`` pattern, for each methods in ``methods``. This is
        a convenient helper over ``add_rule``. For example, this could be used
        to grant all access on the API at once:
        
        >>> ck.add_rules(["GET", "POST", "PUT", "DELETE"], "/*")
        '''
        for method in methods:
            self.add_rule(method, path)

    def add_recursive_rules(self, methods, path):
        '''
        Use this method to grant access on a full API tree. This is the
        recommended way to grant access in the API. It will take care of granted
        the root call *AND* sub-calls for you. Which is commonly forgotten...
        For example, to grant a full access on ``/sms``:

        >>> ck.add_recursive_rules(["GET", "POST", "PUT", "DELETE"], "/sms")
        '''
        path = path.rstrip('*/ ')
        if path:
            self.add_rules(methods, path)
        self.add_rules(methods, path+'/*')

