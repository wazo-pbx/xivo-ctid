#!/usr/bin/python
# vim: set fileencoding=utf-8 :

# Copyright (C) 2012  Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Avencall. See the LICENSE file at top of the source tree
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
from mock import Mock
from mock import patch
from xivo_cti.services import meetme_service_manager
from xivo_cti.dao import meetme_features_dao

find_by_confno = Mock()
get_name = Mock()
has_pin = Mock()
my_time = Mock()


class TestUserServiceManager(unittest.TestCase):

    def test_parse_join(self):
        channel = 'SIP/i7vbu0-00000001'
        number = '800'
        caller_id_name = 'Père Noël'
        caller_id_number = '1000'
        event = {'Event': 'MeetmeJoin',
                 'Privilege': 'call,all',
                 'Channel': channel,
                 'Uniqueid': '1338219287.2',
                 'Meetme': number,
                 'PseudoChan': 'DAHDI/pseudo-965958986',
                 'Admin': 'No',
                 'NoAuthed': 'No',
                 'Usernum': '1',
                 'CallerIDnum': caller_id_number,
                 'CallerIDname': caller_id_name,
                 'ConnectedLineNum': '<unknown>',
                 'ConnectedLineName': '<unknown>'}

        meetme_service_manager.manager = Mock(meetme_service_manager.MeetmeServiceManager)
        meetme_service_manager.parse_join(event)

        meetme_service_manager.manager.join.assert_called_once_with(channel,
                                                                    number,
                                                                    False,
                                                                    1,
                                                                    caller_id_name,
                                                                    caller_id_number)

    @patch('xivo_cti.dao.meetme_features_dao.find_by_confno', find_by_confno)
    @patch('xivo_cti.dao.meetme_features_dao.get_name', get_name)
    @patch('xivo_cti.dao.meetme_features_dao.has_pin', has_pin)
    @patch('time.time', my_time)
    def test_join(self):
        conf_room_name = 'my_test_conf'
        start = 12345.123
        find_by_confno.return_value = 5
        get_name.return_value = conf_room_name
        my_time.return_value = start
        has_pin.return_value = True
        conf_room_number = '800'
        channel = 'SIP/mon_trunk-1234'
        manager = meetme_service_manager.MeetmeServiceManager()

        manager.join(channel, conf_room_number, False, 1, 'Tester 1', '1002')

        expected = {conf_room_number: {'number': conf_room_number,
                                       'name': conf_room_name,
                                       'pin_required': 'Yes',
                                       'start_time': start,
                                       'members': {1: {'join_order': 1,
                                                       'join_time': start,
                                                       'admin': 'No',
                                                       'number': '1002',
                                                       'name': 'Tester 1',
                                                       'channel': channel}}}}

        self.assertEqual(manager._cache, expected)
