# -*- coding: utf-8 -*-

# XiVO CTI Server
#
# Copyright (C) 2007-2012  Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Avencall. See the LICENSE file at top of the souce tree
# or delivered in the installable package in which XiVO CTI Server is
# distributed for more details.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import unittest
from xivo_cti.cti_config import Config
from mock import patch


class TestConfig(unittest.TestCase):

    def test_set_parting(self):
        config = Config([])

        self.assertEqual(config._context_separation, None)

        config.set_context_separation(True)

        self.assertTrue(config._context_separation)

    def test_part_context(self):
        config = Config([])

        config.set_context_separation(True)

        self.assertTrue(config.part_context)

        config.set_context_separation(False)

        self.assertFalse(config.part_context())

    def test_get_var(self):
        config = Config([])
        config.xc_json = {
            'key1': {
                'key12': {
                    'key13': 'var'
                }
            },
            'key2': 'var2'
        }

        expected_result = 'var'

        result = config.get_var('key1', 'key12', 'key13')

        self.assertEquals(result, expected_result)

        expected_result = 'var2'

        result = config.get_var('key2')

        self.assertEquals(result, expected_result)

    def test_get_var_unknow_key(self):
        config = Config([])
        config.xc_json = {
            'key1': {
                'key12': {
                    'key13': 'var'
                }
            },
            'key2': 'var2'
        }

        self.assertRaises(IndexError, config.get_var, 'key1', 'key666')

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

        config = Config([])

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

        config = Config([])

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

        config = Config([])

        result = config._get_profiles()

        mock_get_profiles_dao.assert_called_once_with()

        self.assertEquals(result, expected_result)
