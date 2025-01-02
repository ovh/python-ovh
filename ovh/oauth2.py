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
Thanks to https://github.com/requests/requests-oauthlib/issues/260 for the base used in this file.
"""

from oauthlib.oauth2 import BackendApplicationClient, MissingTokenError, OAuth2Error, TokenExpiredError
from requests_oauthlib import OAuth2Session

from .exceptions import OAuth2FailureError


class RefreshOAuth2Session(OAuth2Session):
    _error = None

    def __init__(self, token_url, **kwargs):
        self.token_url = token_url
        super().__init__(**kwargs)

        # This hijacks the hook mechanism to save details about the last token creation failure.
        # For now, there is no easy other way to access to these details;
        # see https://github.com/requests/requests-oauthlib/pull/441
        self.register_compliance_hook("access_token_response", self.save_error)
        self.register_compliance_hook("refresh_token_response", self.save_error)

    # See __init__, used as compliance hooks
    def save_error(self, resp):
        if 200 <= resp.status_code <= 299:
            self._error = "Received invalid body: " + resp.text
        if resp.status_code >= 400:
            self._error = "Token creation failed with status_code={}, body={}".format(resp.status_code, resp.text)
        return resp

    # Wraps OAuth2Session.fetch_token to enrich returned exception messages, wrapped in an unique class
    def fetch_token(self, *args, **kwargs):
        try:
            return super().fetch_token(*args, **kwargs)
        except MissingTokenError as e:
            desc = "OAuth2 failure: " + e.description
            if self._error:
                desc += " " + self._error

            raise OAuth2FailureError(desc) from e
        except OAuth2Error as e:
            raise OAuth2FailureError("OAuth2 failure: " + str(e)) from e

    # Wraps OAuth2Session.request to handle TokenExpiredError by fetching a new token and retrying
    def request(self, *args, **kwargs):
        try:
            return super().request(*args, **kwargs)
        except TokenExpiredError:
            self.token = self.fetch_token(token_url=self.token_url, **self.auto_refresh_kwargs)
            self.token_updater(self.token)
            return super().request(*args, **kwargs)


class OAuth2:
    _session = None
    _token = None

    def __init__(self, client_id, client_secret, token_url):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = token_url

    def token_updater(self, token):
        self._token = token

    @property
    def session(self):
        if self._session is None:
            self._session = RefreshOAuth2Session(
                token_url=self.token_url,
                client=BackendApplicationClient(
                    client_id=self.client_id,
                    scope=["all"],
                ),
                token=self.token,
                token_updater=self.token_updater,
                auto_refresh_kwargs={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                },
            )
        return self._session

    @property
    def token(self):
        if self._token is None:
            self._token = RefreshOAuth2Session(
                token_url=self.token_url,
                client=BackendApplicationClient(
                    client_id=self.client_id,
                    scope=["all"],
                ),
            ).fetch_token(
                token_url=self.token_url,
                client_id=self.client_id,
                client_secret=self.client_secret,
            )
        return self._token
