# Copyright (c) 2013-2024, OVH SAS.
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

"""
All exceptions used in OVH SDK derives from `APIError`
"""


class APIError(Exception):
    """Base OVH API exception, all specific exceptions inherits from it."""

    def __init__(self, *args, **kwargs):
        self.response = kwargs.pop("response", None)
        if self.response is not None:
            self.query_id = self.response.headers.get("X-OVH-QUERYID")
        else:
            self.query_id = None
        super(APIError, self).__init__(*args, **kwargs)

    def __str__(self):
        if self.query_id:  # pragma: no cover
            return "{} \nOVH-Query-ID: {}".format(super(APIError, self).__str__(), self.query_id)
        else:  # pragma: no cover
            return super(APIError, self).__str__()


class HTTPError(APIError):
    """Raised when the request fails at a low level (DNS, network, ...)"""


class InvalidKey(APIError):
    """Raised when trying to sign request with invalid key"""


class InvalidCredential(APIError):
    """Raised when trying to sign request with invalid consumer key"""


class InvalidConfiguration(APIError):
    """Raised when trying to load an invalid configuration into a client"""


class InvalidResponse(APIError):
    """Raised when api response is not valid json"""


class InvalidRegion(APIError):
    """Raised when region is not in `REGIONS`."""


class ReadOnlyError(APIError):
    """Raised when attempting to modify readonly data."""


class ResourceNotFoundError(APIError):
    """Raised when requested resource does not exist."""


class BadParametersError(APIError):
    """Raised when request contains bad parameters."""


class ResourceConflictError(APIError):
    """Raised when trying to create an already existing resource."""


class NetworkError(APIError):
    """Raised when there is an error from network layer."""


class NotGrantedCall(APIError):
    """Raised when there is an error from network layer."""


class NotCredential(APIError):
    """Raised when there is an error from network layer."""


class Forbidden(APIError):
    """Raised when there is an error from network layer."""


class ResourceExpiredError(APIError):
    """Raised when requested resource expired."""


class OAuth2FailureError(APIError):
    """Raised when the OAuth2 workflow fails"""
