# -*- coding: utf-8 -*-
# Copyright (C) 2007-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

import unittest

from xivo_cti.cti_config import _DbConfig as Config
from mock import patch


class TestConfig(unittest.TestCase):

    @patch('xivo_dao.cti_service_dao.get_services')
    def test_get_services(self, mock_get_services_dao):
        expected_result = {
            "itm_services_agent": [""],
            "itm_services_client": ["enablednd",
                                    "fwdunc",
                                    "fwdbusy",
                                    "fwdrna"]
        }

        mock_get_services_dao.return_value = {
            "agent": [],
            "client": ["enablednd",
                       "fwdunc",
                       "fwdbusy",
                       "fwdrna"]
        }

        config = Config()

        result = config._get_services()

        mock_get_services_dao.assert_called_once_with()

        self.assertEquals(result, expected_result)

    @patch('xivo_dao.cti_preference_dao.get_preferences')
    def test_get_preferences(self, mock_get_preferences_dao):
        expected_result = {
            "itm_preferences_agent": False,
            "itm_preferences_client": {
                "xlet.identity.logagent": "1",
                "xlet.identity.pauseagent": "1"
            }
        }

        mock_get_preferences_dao.return_value = {
            "agent": {},
            "client": {
                "xlet.identity.logagent": "1",
                "xlet.identity.pauseagent": "1"
            }
        }

        config = Config()

        result = config._get_preferences()

        mock_get_preferences_dao.assert_called_once_with()

        self.assertEquals(result, expected_result)

    @patch('xivo_dao.cti_profile_dao.get_profiles')
    def test_get_profiles(self, mock_get_profiles_dao):
        expected_result = {
            "client": {
                "name": "Client",
                "phonestatus": "xivo",
                "userstatus": "xivo",
                "preferences": "itm_preferences_client",
                "services": "itm_services_client",
                "xlets": [
                    [
                        "tabber",
                        "grid",
                        "1"
                    ],
                    [
                        "agentdetails",
                        "dock",
                        "cms"
                    ]
                ]
            }
        }

        mock_get_profiles_dao.return_value = {
            "client": {
                "name": "Client",
                "phonestatus": "xivo",
                "userstatus": "xivo",
                "preferences": "itm_preferences_client",
                "services": "itm_services_client",
                "xlets": [
                    {'name': 'tabber',
                     'layout': 'grid',
                     'floating': True,
                     'closable': True,
                     'movable': True,
                     'scrollable': True,
                     'order': 1},
                    {'name': 'agentdetails',
                     'layout': 'dock',
                     'floating': False,
                     'closable': True,
                     'movable': True,
                     'scrollable': True,
                     'order': 0}
                ]
            }
        }

        config = Config()

        result = config._get_profiles()

        mock_get_profiles_dao.assert_called_once_with()

        self.assertEquals(result, expected_result)
