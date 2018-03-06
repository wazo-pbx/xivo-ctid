# -*- coding: utf-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

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
