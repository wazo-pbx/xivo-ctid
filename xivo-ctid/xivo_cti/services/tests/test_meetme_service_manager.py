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
import copy
from mock import Mock
from mock import patch
from xivo_cti.services import meetme_service_manager

find_by_confno = Mock()
get_name = Mock()
has_pin = Mock()
my_time = Mock()
get_configs = Mock()
get_config = Mock()


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

    @patch('xivo_cti.dao.meetme_features_dao.get_config', get_config)
    @patch('xivo_cti.dao.meetme_features_dao.find_by_confno', find_by_confno)
    @patch('time.time', my_time)
    def test_join(self):
        conf_room_number = '800'
        conf_room_name = 'my_test_conf'
        start = 12345.123
        channel = 'SIP/mon_trunk-1234'

        find_by_confno.return_value = 5
        get_config.return_value = (conf_room_name, conf_room_number, True)
        my_time.return_value = start

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

    @patch('time.time', my_time)
    @patch('xivo_cti.dao.meetme_features_dao.get_config', get_config)
    @patch('xivo_cti.dao.meetme_features_dao.find_by_confno', find_by_confno)
    def test_join_second(self):
        start_time = 12345678.123
        join_time = 12345699.123
        phone_number = '4185551234'
        channel = 'SIP/pcm_dev-0000005d'
        conf_room_number = '800'
        conf_room_name = 'my_test_conf'

        my_time.return_value = start_time
        find_by_confno.return_value = 4
        get_config.return_value = (conf_room_name, conf_room_number, True)

        manager = meetme_service_manager.MeetmeServiceManager()
        manager._cache = {conf_room_number: {'number': conf_room_number,
                                              'name': conf_room_name,
                                              'pin_required': 'Yes',
                                              'start_time': start_time,
                                              'members': {1: {'join_order': 1,
                                                              'join_time': start_time,
                                                              'admin': 'No',
                                                              'number': '1002',
                                                              'name': 'Tester 1',
                                                              'channel': '123'}}}}

        my_time.return_value = join_time
        manager.join(channel, conf_room_number, True, 2, phone_number, phone_number)
        result = manager._cache

        expected = {conf_room_number: {'number': conf_room_number,
                                       'name': conf_room_name,
                                       'pin_required': 'Yes',
                                       'start_time': start_time,
                                       'members': {1: {'join_order': 1,
                                                       'join_time': start_time,
                                                       'admin': 'No',
                                                       'number': '1002',
                                                       'name': 'Tester 1',
                                                       'channel': '123'},
                                                   2: {'join_order': 2,
                                                       'join_time': join_time,
                                                       'admin': 'Yes',
                                                       'number': phone_number,
                                                       'name': phone_number,
                                                       'channel': channel}}}}
        self.assertEqual(result, expected)

    @patch('time.time', my_time)
    def test_build_joining_member_status(self):
        channel = 'SIP/kjsdfh-12356'
        my_time.return_value = 1234.1234
        result = meetme_service_manager._build_joining_member_status(1, True, 'Tester One', '666', channel)
        expected = {'join_order': 1,
                    'join_time': 1234.1234,
                    'admin': 'Yes',
                    'number': '666',
                    'name': 'Tester One',
                    'channel': channel}

        self.assertEqual(result, expected)

    @patch('xivo_cti.dao.meetme_features_dao.find_by_confno', find_by_confno)
    @patch('xivo_cti.dao.meetme_features_dao.get_config', get_config)
    def test_set_room_config(self):
        conf_room_number = '800'
        conf_room_name = 'test'

        find_by_confno.return_value = 2
        get_config.return_value = (conf_room_name, conf_room_number, True)

        manager = meetme_service_manager.MeetmeServiceManager()
        manager._set_room_config(conf_room_number)

        result = manager._cache

        expected = {conf_room_number: {'name': conf_room_name,
                                       'number': conf_room_number,
                                       'pin_required': 'Yes',
                                       'start_time': 0,
                                       'members': {}}}

        self.assertEqual(result, expected)

    def test_parse_leave(self):
        event = {'Event': 'MeetmeLeave',
                 'Privilege': 'call,all',
                 'Channel': 'SIP/i7vbu0-00000000',
                 'Uniqueid': '1338219251.0',
                 'Meetme': '800',
                 'Usernum': '1',
                 'CallerIDNum': '1000',
                 'CallerIDName': 'Père Noël',
                 'ConnectedLineNum': '<unknown>',
                 'ConnectedLineName': '<unknown>',
                 'Duration': '31'}

        manager = Mock(meetme_service_manager.MeetmeServiceManager)
        meetme_service_manager.manager = manager

        meetme_service_manager.parse_leave(event)

        manager.leave.assert_called_once_with('800', 1)

    def test_leave(self):
        conf_room_number = '800'
        conf_room_name = 'my_test_conf'
        start_time = 1234556.123

        manager = meetme_service_manager.MeetmeServiceManager()

        manager._cache = {conf_room_number: {'number': conf_room_number,
                                            'name': conf_room_name,
                                            'pin_required': 'Yes',
                                            'start_time': start_time,
                                            'members': {1: {'join_order': 1,
                                                            'join_time': start_time,
                                                            'admin': 'No',
                                                            'number': '1002',
                                                            'name': 'Tester 1',
                                                            'channel': 'SIP/jsdhfjd-124'},
                                                        2: {'join_order': 2,
                                                            'join_time': start_time + 10,
                                                            'admin': 'Yes',
                                                            'number': '4181235555',
                                                            'name': '4181235555',
                                                            'channel': 'DAHDI/i1/4181235555-5'}}}}

        manager.leave('800', 1)

        expected = {conf_room_number: {'number': conf_room_number,
                                       'name': conf_room_name,
                                       'pin_required': 'Yes',
                                       'start_time': start_time,
                                       'members': {2: {'join_order': 2,
                                                       'join_time': start_time + 10,
                                                       'admin': 'Yes',
                                                       'number': '4181235555',
                                                       'name': '4181235555',
                                                       'channel': 'DAHDI/i1/4181235555-5'}}}}

        self.assertEqual(manager._cache, expected)

        manager.leave('800', 2)

        expected = {conf_room_number: {'number': conf_room_number,
                                       'name': conf_room_name,
                                       'pin_required': 'Yes',
                                       'start_time': 0,
                                       'members': {}}}

        self.assertEqual(manager._cache, expected)

    def test_has_member(self):
        manager = meetme_service_manager.MeetmeServiceManager()
        manager._cache = {'800': {'members': {}}}

        self.assertFalse(manager._has_members('800'))

        manager._cache = {'800': {'number': '800',
                                  'name': 'conf',
                                  'pin_required': 'Yes',
                                  'start_time': 12345.21,
                                  'members': {2: {'join_order': 2,
                                                  'join_time': 1235.123,
                                                  'admin': 'Yes',
                                                  'number': '4181235555',
                                                  'name': '4181235555',
                                                  'channel': 'DAHDI/i1/4181235555-5'}}}}

        self.assertTrue(manager._has_members('800'))

    @patch('xivo_cti.dao.meetme_features_dao.get_config', get_config)
    @patch('xivo_cti.dao.meetme_features_dao.find_by_confno', find_by_confno)
    @patch('time.time', my_time)
    def test_join_when_empty(self):
        conf_room_number = '800'
        conf_room_name = 'my_test_conf'
        channel = 'SIP/kljfh-1234'
        join_time = 12345.654

        my_time.return_value = join_time
        find_by_confno.return_value = 2
        get_config.return_value = (conf_room_name, conf_room_number, True)

        manager = meetme_service_manager.MeetmeServiceManager()
        manager._cache = {conf_room_number: {'number': conf_room_number,
                                             'name': conf_room_name,
                                             'pin_required': 'Yes',
                                             'start_time': 0,
                                             'members': {}}}

        manager.join(channel, conf_room_number, False, 1, 'Tester 1', '1002')

        expected = {conf_room_number: {'number': conf_room_number,
                                       'name': conf_room_name,
                                       'pin_required': 'Yes',
                                       'start_time': join_time,
                                       'members': {1: {'join_order': 1,
                                                       'join_time': join_time,
                                                       'admin': 'No',
                                                       'number': '1002',
                                                       'name': 'Tester 1',
                                                       'channel': channel}}}}

        self.assertEqual(manager._cache, expected)

    @patch('xivo_cti.dao.meetme_features_dao.get_configs', get_configs)
    def test_initial_state(self):
        get_configs.return_value = [('Conference1', '9000', True),
                                    ('Conference2', '9001', False),
                                    ('Conference3', '9002', False)]

        manager = meetme_service_manager.MeetmeServiceManager()
        manager._initialize_configs()

        expected = {'9000': {'number': '9000',
                             'name': 'Conference1',
                             'pin_required': 'Yes',
                             'start_time': 0,
                             'members': {}},
                    '9001': {'number': '9001',
                             'name': 'Conference2',
                             'pin_required': 'No',
                             'start_time': 0,
                             'members': {}},
                    '9002': {'number': '9002',
                             'name': 'Conference3',
                             'pin_required': 'No',
                             'start_time': 0,
                             'members': {}}}

        self.assertEqual(manager._cache, expected)

    def test_add_room(self):
        manager = meetme_service_manager.MeetmeServiceManager()

        manager._add_room('Conference1', '9000', True)

        expected = {'9000': {'number': '9000',
                             'name': 'Conference1',
                             'pin_required': 'Yes',
                             'start_time': 0,
                             'members': {}}}

        self.assertEqual(manager._cache, expected)

    def test_parse_meetmelist(self):
        channel = 'SIP/pcm_dev-00000003'
        event = {'Event': 'MeetmeList',
                 'Conference': '800',
                 'UserNumber': '1',
                 'CallerIDNum': '666',
                 'CallerIDName': 'My Name',
                 'ConnectedLineNum': '<unknown>',
                 'ConnectedLineName': '<noname>',
                 'Channel': channel,
                 'Admin': 'No',
                 'Role': 'Talkandlisten',
                 'MarkedUser': 'No',
                 'Muted': 'No',
                 'Talking': 'Notmonitored'}

        manager = Mock(meetme_service_manager.MeetmeServiceManager)
        meetme_service_manager.manager = manager

        meetme_service_manager.parse_meetmelist(event)

        manager.refresh.assert_called_once_with(channel, '800', False, 1, 'My Name', '666')

    @patch('xivo_cti.dao.meetme_features_dao.get_config', get_config)
    @patch('xivo_cti.dao.meetme_features_dao.find_by_confno', find_by_confno)
    def test_refresh_empty(self):
        channel = 'DAHDI/i1/5555555555-1'
        conf_no = '800'
        conf_name = 'My conf'
        name = 'First Testeur'
        number = '5555555555'

        find_by_confno.return_value = 1
        get_config.return_value = (conf_name, conf_no, False)

        manager = meetme_service_manager.MeetmeServiceManager()

        manager.refresh(channel, conf_no, False, 1, name, number)

        expected = {conf_no: {'number': conf_no,
                              'name': conf_name,
                              'pin_required': 'No',
                              'start_time': -1,
                              'members': {1: {'join_order': 1,
                                              'join_time': -1,
                                              'admin': 'No',
                                              'number': number,
                                              'name': name,
                                              'channel': channel}}}}

        self.assertEqual(manager._cache, expected)

    def test_refresh_already_there(self):
        manager = meetme_service_manager.MeetmeServiceManager()
        name, number = 'Tester One', '6666'
        channel = 'SIP/khsdfjkld-1234'

        manager._cache['800'] = {'number': '800',
                                 'name': 'test',
                                 'pin_required': 'No',
                                 'start_time': 1238934.12342,
                                 'members': {1: {'join_order': 1,
                                                 'join_time': 1238934.12342,
                                                 'admin': 'No',
                                                 'number': number,
                                                 'name': name,
                                                 'channel': channel}}}

        expected = copy.deepcopy(manager._cache)

        manager.refresh(channel, '800', False, 1, name, number)

        self.assertEqual(manager._cache, expected)

    def test_has_member(self):
        manager = meetme_service_manager.MeetmeServiceManager()

        self.assertFalse(manager._has_member('800', 1, 'Tester One', '1234'))

        manager._cache = {'800': {'members': {1: {'name': 'Tester One',
                                                  'number': '1234'}}}}

        self.assertTrue(manager._has_member('800', 1, 'Tester One', '1234'))
