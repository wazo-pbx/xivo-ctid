# -*- coding: utf-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

import os
import pprint
import requests

from hamcrest import assert_that, empty

from xivo_test_helpers.asset_launching_test_case import AssetLaunchingTestCase


class TestDocumentation(AssetLaunchingTestCase):

    service = 'ctid'
    asset = 'documentation'
    assets_root = os.path.join(os.path.dirname(__file__), '..', 'assets')

    def test_documentation_errors(self):
        ctid_port = self.service_port(9495, 'ctid')
        api_url = 'http://localhost:{port}/0.1/api/api.yml'.format(port=ctid_port)
        api = requests.get(api_url)
        self.validate_api(api)

    def validate_api(self, api):
        validator_port = self.service_port(8080, 'swagger-validator')
        validator_url = 'http://localhost:{port}/debug'.format(port=validator_port)
        response = requests.post(validator_url, data=api)
        assert_that(response.json(), empty(), pprint.pformat(response.json()))
