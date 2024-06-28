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

from configparser import MissingSectionHeaderError
import os
from pathlib import Path
from unittest.mock import patch

import pytest

import ovh
from ovh.exceptions import InvalidConfiguration, InvalidRegion

TEST_DATA = str(Path(__file__).resolve().parent / "data")
systemConf = TEST_DATA + "/system.ini"
userPartialConf = TEST_DATA + "/userPartial.ini"
userConf = TEST_DATA + "/user.ini"
userOAuth2Conf = TEST_DATA + "/user_oauth2.ini"
userOAuth2InvalidConf = TEST_DATA + "/user_oauth2_invalid.ini"
userOAuth2IncompatibleConfig = TEST_DATA + "/user_oauth2_incompatible.ini"
userBothConf = TEST_DATA + "/user_both.ini"
localPartialConf = TEST_DATA + "/localPartial.ini"
doesNotExistConf = TEST_DATA + "/doesNotExist.ini"
invalidINIConf = TEST_DATA + "/invalid.ini"
errorConf = TEST_DATA


class TestConfig:
    def test_real_lookup_path(self):
        home = os.environ["HOME"]
        pwd = os.environ["PWD"]

        assert ovh.config.CONFIG_PATH == [
            "/etc/ovh.conf",
            home + "/.ovh.conf",
            pwd + "/ovh.conf",
        ]

    @patch("ovh.config.CONFIG_PATH", [systemConf, userPartialConf, localPartialConf])
    def test_config_from_files(self):
        client = ovh.Client(endpoint="ovh-eu")
        assert client._application_key == "system"
        assert client._application_secret == "user"
        assert client._consumer_key == "local"

    @patch("ovh.config.CONFIG_PATH", [userConf])
    def test_config_from_given_config_file(self):
        client = ovh.Client(endpoint="ovh-eu", config_file=systemConf)
        assert client._application_key == "system"
        assert client._application_secret == "system"
        assert client._consumer_key == "system"

    @patch("ovh.config.CONFIG_PATH", [userConf])
    def test_config_from_only_one_file(self):
        client = ovh.Client(endpoint="ovh-eu")
        assert client._application_key == "user"
        assert client._application_secret == "user"
        assert client._consumer_key == "user"

    @patch("ovh.config.CONFIG_PATH", [doesNotExistConf])
    def test_config_from_non_existing_file(self):
        with pytest.raises(InvalidConfiguration) as e:
            ovh.Client(endpoint="ovh-eu")

        assert str(e.value) == (
            "Missing authentication information, you need to provide at least an "
            "application_key/application_secret or a client_id/client_secret"
        )

    @patch("ovh.config.CONFIG_PATH", [invalidINIConf])
    def test_config_from_invalid_ini_file(self):
        with pytest.raises(MissingSectionHeaderError):
            ovh.Client(endpoint="ovh-eu")

    @patch("ovh.config.CONFIG_PATH", [errorConf])
    def test_config_from_invalid_file(self):
        with pytest.raises(InvalidConfiguration) as e:
            ovh.Client(endpoint="ovh-eu")

        assert str(e.value) == (
            "Missing authentication information, you need to provide at least an "
            "application_key/application_secret or a client_id/client_secret"
        )

    @patch("ovh.config.CONFIG_PATH", [userOAuth2Conf])
    def test_config_oauth2(self):
        client = ovh.Client(endpoint="ovh-eu")
        assert client._client_id == "foo"
        assert client._client_secret == "bar"

    @patch("ovh.config.CONFIG_PATH", [userBothConf])
    def test_config_invalid_both(self):
        with pytest.raises(InvalidConfiguration) as e:
            ovh.Client(endpoint="ovh-eu")

        assert str(e.value) == "Can't use both application_key/application_secret and OAuth2 client_id/client_secret"

    @patch("ovh.config.CONFIG_PATH", [userOAuth2InvalidConf])
    def test_config_invalid_oauth2(self):
        with pytest.raises(InvalidConfiguration) as e:
            ovh.Client(endpoint="ovh-eu")

        assert str(e.value) == "Invalid OAuth2 config, both client_id and client_secret must be given"

    @patch("ovh.config.CONFIG_PATH", [userOAuth2IncompatibleConfig])
    def test_config_incompatible_oauth2(self):
        with pytest.raises(InvalidConfiguration) as e:
            ovh.Client(endpoint="kimsufi-eu")

        assert str(e.value) == (
            "OAuth2 authentication is not compatible with endpoint kimsufi-eu "
            + "(it can only be used with ovh-eu, ovh-ca and ovh-us)"
        )

    @patch("ovh.config.CONFIG_PATH", [userConf])
    @patch.dict(
        "os.environ",
        {
            "OVH_ENDPOINT": "ovh-eu",
            "OVH_APPLICATION_KEY": "env",
            "OVH_APPLICATION_SECRET": "env",
            "OVH_CONSUMER_KEY": "env",
        },
    )
    def test_config_from_env(self):
        client = ovh.Client(endpoint="ovh-eu")
        assert client._application_key == "env"
        assert client._application_secret == "env"
        assert client._consumer_key == "env"

    @patch("ovh.config.CONFIG_PATH", [userConf])
    def test_config_from_args(self):
        client = ovh.Client(
            endpoint="ovh-eu", application_key="param", application_secret="param", consumer_key="param"
        )
        assert client._application_key == "param"
        assert client._application_secret == "param"
        assert client._consumer_key == "param"

    def test_invalid_endpoint(self):
        with pytest.raises(InvalidRegion):
            ovh.Client(endpoint="not_existing")
