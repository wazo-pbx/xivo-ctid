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
from xivo_cti.services.meetme import service_manager
from xivo_cti.services.meetme import service_notifier

find_by_confno = Mock()
get_name = Mock()
has_pin = Mock()
my_time = Mock()
get_configs = Mock()
get_config = Mock()
muted_on_join_by_number = Mock()
get_cid_for_channel = Mock()
conf_room_number = '800'
conf_room_name = 'test_conf'


class TestUserServiceManager(unittest.TestCase):

    def setUp(self):
        self.publish = Mock()
        self.manager = service_manager.MeetmeServiceManager()

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

        service_manager.manager = Mock(service_manager.MeetmeServiceManager)
        service_manager.parse_join(event)

        service_manager.manager.join.assert_called_once_with(channel,
                                                             number,
                                                             1,
                                                             caller_id_name,
                                                             caller_id_number)

    @patch('xivo_cti.dao.meetme_features_dao.get_config', get_config)
    @patch('xivo_cti.dao.meetme_features_dao.find_by_confno', find_by_confno)
    @patch('xivo_cti.dao.meetme_features_dao.muted_on_join_by_number', muted_on_join_by_number)
    @patch('time.time', my_time)
    def test_join(self):
        start = 12345.123
        channel = 'SIP/mon_trunk-1234'

        find_by_confno.return_value = 5
        get_config.return_value = (conf_room_name, conf_room_number, True, 'default')
        my_time.return_value = start
        muted_on_join_by_number.return_value = True

        self.manager._publish_change = self.publish

        self.manager.join(channel, conf_room_number, 1, 'Tester 1', '1002')

        expected = {conf_room_number: {'number': conf_room_number,
                                       'name': conf_room_name,
                                       'pin_required': True,
                                       'start_time': start,
                                       'context': 'default',
                                       'members': {1: {'join_order': 1,
                                                       'join_time': start,
                                                       'number': '1002',
                                                       'name': 'Tester 1',
                                                       'channel': channel,
                                                       'muted': True}}}}

        self.assertEqual(self.manager._cache, expected)
        self.publish.assert_called_once_with()

    @patch('time.time', my_time)
    @patch('xivo_cti.dao.meetme_features_dao.get_config', get_config)
    @patch('xivo_cti.dao.meetme_features_dao.find_by_confno', find_by_confno)
    @patch('xivo_cti.dao.meetme_features_dao.muted_on_join_by_number', muted_on_join_by_number)
    def test_join_second(self):
        start_time = 12345678.123
        join_time = 12345699.123
        phone_number = '4185551234'
        channel = 'SIP/pcm_dev-0000005d'

        my_time.return_value = start_time
        find_by_confno.return_value = 4
        get_config.return_value = (conf_room_name, conf_room_number, True, 'test')
        muted_on_join_by_number.return_value = True

        self.manager._publish_change = self.publish
        self.manager._cache = {conf_room_number: {'number': conf_room_number,
                                                  'name': conf_room_name,
                                                  'pin_required': True,
                                                  'start_time': start_time,
                                                  'members': {1: {'join_order': 1,
                                                                 'join_time': start_time,
                                                                 'number': '1002',
                                                                 'name': 'Tester 1',
                                                                 'channel': '123',
                                                                 'muted': False}}}}

        my_time.return_value = join_time
        self.manager.join(channel, conf_room_number, 2, phone_number, phone_number)
        result = self.manager._cache

        expected = {conf_room_number: {'number': conf_room_number,
                                       'name': conf_room_name,
                                       'pin_required': True,
                                       'start_time': start_time,
                                       'members': {1: {'join_order': 1,
                                                       'join_time': start_time,
                                                       'number': '1002',
                                                       'name': 'Tester 1',
                                                       'channel': '123',
                                                       'muted': False},
                                                   2: {'join_order': 2,
                                                       'join_time': join_time,
                                                       'number': phone_number,
                                                       'name': phone_number,
                                                       'channel': channel,
                                                       'muted': True}}}}
        self.assertEqual(result, expected)
        self.publish.assert_called_once_with()

    def test_build_member_status(self):
        channel = 'SIP/kjsdfh-12356'
        result = service_manager._build_member_status(1, 'Tester One', '666', channel, True)
        expected = {'join_order': 1,
                    'join_time': -1,
                    'number': '666',
                    'name': 'Tester One',
                    'channel': channel,
                    'muted': True}

        self.assertEqual(result, expected)

    @patch('time.time', my_time)
    def test_build_joining_member_status(self):
        channel = 'SIP/kjsdfh-12356'
        my_time.return_value = 1234.1234
        result = service_manager._build_joining_member_status(1, 'Tester One', '666', channel, False)
        expected = {'join_order': 1,
                    'join_time': 1234.1234,
                    'number': '666',
                    'name': 'Tester One',
                    'channel': channel,
                    'muted': False}

        self.assertEqual(result, expected)

    @patch('xivo_cti.dao.meetme_features_dao.find_by_confno', find_by_confno)
    @patch('xivo_cti.dao.meetme_features_dao.get_config', get_config)
    def test_set_room_config(self):
        find_by_confno.return_value = 2
        get_config.return_value = (conf_room_name, conf_room_number, True, 'my_context')

        self.manager._set_room_config(conf_room_number)

        result = self.manager._cache

        expected = {conf_room_number: {'name': conf_room_name,
                                       'number': conf_room_number,
                                       'pin_required': True,
                                       'start_time': 0,
                                       'context': 'my_context',
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

        manager = Mock(service_manager.MeetmeServiceManager)
        service_manager.manager = manager

        service_manager.parse_leave(event)

        manager.leave.assert_called_once_with('800', 1)

    def test_leave(self):
        start_time = 1234556.123

        self.manager._publish_change = self.publish

        self.manager._cache = {conf_room_number: {'number': conf_room_number,
                                                  'name': conf_room_name,
                                                  'pin_required': True,
                                                  'start_time': start_time,
                                                  'members': {1: {'join_order': 1,
                                                                  'join_time': start_time,
                                                                  'number': '1002',
                                                                  'name': 'Tester 1',
                                                                  'channel': 'SIP/jsdhfjd-124'},
                                                              2: {'join_order': 2,
                                                                  'join_time': start_time + 10,
                                                                  'number': '4181235555',
                                                                  'name': '4181235555',
                                                                  'channel': 'DAHDI/i1/4181235555-5'}}}}

        self.manager.leave('800', 1)

        self.publish.assert_called_once_with()
        self.publish.reset_mock()

        expected = {conf_room_number: {'number': conf_room_number,
                                       'name': conf_room_name,
                                       'pin_required': True,
                                       'start_time': start_time,
                                       'members': {2: {'join_order': 2,
                                                       'join_time': start_time + 10,
                                                       'number': '4181235555',
                                                       'name': '4181235555',
                                                       'channel': 'DAHDI/i1/4181235555-5'}}}}

        self.assertEqual(self.manager._cache, expected)

        self.manager.leave('800', 2)

        expected = {conf_room_number: {'number': conf_room_number,
                                       'name': conf_room_name,
                                       'pin_required': True,
                                       'start_time': 0,
                                       'members': {}}}

        self.assertEqual(self.manager._cache, expected)
        self.publish.assert_called_once_with()

    def test_has_members(self):
        self.manager._cache = {'800': {'members': {}}}

        self.assertFalse(self.manager._has_members('800'))

        self.manager._cache = {'800': {'number': '800',
                                       'name': 'conf',
                                       'pin_required': True,
                                       'start_time': 12345.21,
                                       'members': {2: {'join_order': 2,
                                                      'join_time': 1235.123,
                                                      'number': '4181235555',
                                                      'name': '4181235555',
                                                      'channel': 'DAHDI/i1/4181235555-5'}}}}

        self.assertTrue(self.manager._has_members('800'))

    @patch('xivo_cti.dao.meetme_features_dao.get_config', get_config)
    @patch('xivo_cti.dao.meetme_features_dao.find_by_confno', find_by_confno)
    @patch('xivo_cti.dao.meetme_features_dao.muted_on_join_by_number', muted_on_join_by_number)
    @patch('time.time', my_time)
    def test_join_when_empty(self):
        channel = 'SIP/kljfh-1234'
        join_time = 12345.654

        my_time.return_value = join_time
        find_by_confno.return_value = 2
        get_config.return_value = (conf_room_name, conf_room_number, True, 'default')
        muted_on_join_by_number.return_value = False

        self.manager._cache = {conf_room_number: {'number': conf_room_number,
                                                  'name': conf_room_name,
                                                  'pin_required': True,
                                                  'start_time': 0,
                                                  'members': {}}}

        self.manager.join(channel, conf_room_number, 1, 'Tester 1', '1002')

        expected = {conf_room_number: {'number': conf_room_number,
                                       'name': conf_room_name,
                                       'pin_required': True,
                                       'start_time': join_time,
                                       'members': {1: {'join_order': 1,
                                                       'join_time': join_time,
                                                       'number': '1002',
                                                       'name': 'Tester 1',
                                                       'channel': channel,
                                                       'muted': False}}}}

        self.assertEqual(self.manager._cache, expected)

    @patch('xivo_cti.dao.meetme_features_dao.get_configs', get_configs)
    def test_initial_state(self):
        get_configs.return_value = [('Conference1', '9000', True, 'default'),
                                    ('Conference2', '9001', False, 'test'),
                                    ('Conference3', '9002', False, 'test')]

        self.manager._publish_change = self.publish
        self.manager.initialize()

        expected = {'9000': {'number': '9000',
                             'name': 'Conference1',
                             'pin_required': True,
                             'start_time': 0,
                             'context': 'default',
                             'members': {}},
                    '9001': {'number': '9001',
                             'name': 'Conference2',
                             'pin_required': False,
                             'start_time': 0,
                             'context': 'test',
                             'members': {}},
                    '9002': {'number': '9002',
                             'name': 'Conference3',
                             'pin_required': False,
                             'start_time': 0,
                             'context': 'test',
                             'members': {}}}

        self.assertEqual(self.manager._cache, expected)
        self.publish.assert_called_once_with()

    def test_add_room(self):
        self.manager._add_room('Conference1', '9000', True, 'ctx')

        expected = {'9000': {'number': '9000',
                             'name': 'Conference1',
                             'pin_required': True,
                             'start_time': 0,
                             'context': 'ctx',
                             'members': {}}}

        self.assertEqual(self.manager._cache, expected)

    @patch('xivo_cti.dao.meetme_features_dao.get_configs', get_configs)
    def test_initialize_configs_with_members(self):
        get_configs.return_value = [('Conference2', '9001', False, 'test'),
                                    ('Conference3', '9002', False, 'test')]

        members_9001 = {1: {'join_order': 1,
                            'join_time': 1234.1235,
                            'number': '1002',
                            'name': 'Tester 1',
                            'channel': 'sip/123',
                            'muted': False}}

        self.manager._cache = {'9000': {'number': '9000',
                                        'name': 'Conference1',
                                        'pin_required': True,
                                        'start_time': 0,
                                        'context': 'default',
                                        'members': {}},
                               '9001': {'number': '9001',
                                        'name': 'Conference2',
                                        'pin_required': False,
                                        'start_time': 0,
                                        'context': 'test',
                                        'members': members_9001}}

        self.manager.initialize()

        expected = {'9002': {'number': '9002',
                             'name': 'Conference3',
                             'pin_required': False,
                             'start_time': 0,
                             'context': 'test',
                             'members': {}},
                    '9001': {'number': '9001',
                             'name': 'Conference2',
                             'pin_required': False,
                             'start_time': 0,
                             'context': 'test',
                             'members': members_9001}}

        self.assertEqual(self.manager._cache, expected)

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

        manager = Mock(service_manager.MeetmeServiceManager)
        service_manager.manager = manager

        service_manager.parse_meetmelist(event)

        manager.refresh.assert_called_once_with(channel, '800', 1, 'My Name', '666', False)

    @patch('xivo_cti.dao.meetme_features_dao.get_config', get_config)
    @patch('xivo_cti.dao.meetme_features_dao.find_by_confno', find_by_confno)
    def test_refresh_empty(self):
        channel = 'DAHDI/i1/5555555555-1'
        conf_no = '800'
        conf_name = 'My conf'
        name = 'First Testeur'
        number = '5555555555'

        find_by_confno.return_value = 1
        get_config.return_value = (conf_name, conf_no, False, 'dev')

        self.manager._publish_change = self.publish

        self.manager.refresh(channel, conf_no, 1, name, number, is_muted=True)

        expected = {conf_no: {'number': conf_no,
                              'name': conf_name,
                              'pin_required': False,
                              'start_time': -1,
                              'context': 'dev',
                              'members': {1: {'join_order': 1,
                                              'join_time': -1,
                                              'number': number,
                                              'name': name,
                                              'channel': channel,
                                              'muted': True}}}}

        self.assertEqual(self.manager._cache, expected)
        self.publish.assert_called_once_with()

    def test_refresh_already_there(self):
        name, number = 'Tester One', '6666'
        channel = 'SIP/khsdfjkld-1234'

        self.manager._cache['800'] = {'number': '800',
                                      'name': 'test',
                                      'pin_required': False,
                                      'start_time': 1238934.12342,
                                      'members': {1: {'join_order': 1,
                                                      'join_time': 1238934.12342,
                                                      'number': number,
                                                      'name': name,
                                                      'channel': channel,
                                                      'muted': False}}}

        expected = copy.deepcopy(self.manager._cache)

        self.manager.refresh(channel, '800', 1, name, number, False)

        self.assertEqual(self.manager._cache, expected)

    def test_has_member(self):
        self.assertFalse(self.manager._has_member('800', 1, 'Tester One', '1234'))

        self.manager._cache = {'800': {'members': {1: {'name': 'Tester One',
                                                       'number': '1234'}}}}

        self.assertTrue(self.manager._has_member('800', 1, 'Tester One', '1234'))

    def test_muting(self):
        self.manager._publish_change = self.publish

        try:
            self.manager.mute(conf_room_number, 1)
        except Exception:
            self.assertTrue(False)

        self.manager._cache = {conf_room_number: {'number': conf_room_number,
                                                  'name': conf_room_name,
                                                  'pin_required': True,
                                                  'start_time': 1234.1234,
                                                  'members': {1: {'join_order': 1,
                                                                  'join_time': 1234.1234,
                                                                  'number': '1002',
                                                                  'name': 'Tester 1',
                                                                  'channel': 'SIP/jsdhfjd-124',
                                                                  'muted': False},
                                                              2: {'join_order': 2,
                                                                  'join_time': 1239.1234,
                                                                  'number': '4181235555',
                                                                  'name': '4181235555',
                                                                  'channel': 'DAHDI/i1/4181235555-5',
                                                                  'muted': False}}}}

        expected = copy.deepcopy(self.manager._cache)
        expected[conf_room_number]['members'][2]['muted'] = True

        self.manager.mute(conf_room_number, 2)

        self.assertEqual(self.manager._cache, expected)
        self.publish.assert_called_once_with()

    def test_unmuting(self):
        self.manager._publish_change = self.publish

        try:
            self.manager.unmute(conf_room_number, 1)
        except Exception:
            self.assertTrue(False)

        self.manager._cache = {conf_room_number: {'number': conf_room_number,
                                                  'name': conf_room_name,
                                                  'pin_required': True,
                                                  'start_time': 1234.1234,
                                                  'members': {1: {'join_order': 1,
                                                                  'join_time': 1234.1234,
                                                                  'number': '1002',
                                                                  'name': 'Tester 1',
                                                                  'channel': 'SIP/jsdhfjd-124',
                                                                  'muted': False},
                                                              2: {'join_order': 2,
                                                                  'join_time': 1239.1234,
                                                                  'number': '4181235555',
                                                                  'name': '4181235555',
                                                                  'channel': 'DAHDI/i1/4181235555-5',
                                                                  'muted': True}}}}

        expected = copy.deepcopy(self.manager._cache)
        expected[conf_room_number]['members'][2]['muted'] = False

        self.manager.unmute(conf_room_number, 2)

        self.assertEqual(self.manager._cache, expected)
        self.publish.assert_called_once_with()

    def test_parse_mute(self):
        event = {'Event': 'MeetmeMute',
                 'Privilege': 'call,all',
                 'Channel': 'SIP/pcm_dev-0000000b',
                 'Uniqueid': '1338379282.18',
                 'Meetme': '800',
                 'Usernum': '1',
                 'Status': 'on'}

        manager = Mock(service_manager.MeetmeServiceManager)
        service_manager.manager = manager

        service_manager.parse_meetmemute(event)

        manager.mute.assert_called_once_with('800', 1)

    def test_parse_unmute(self):
        event = {'Event': 'MeetmeMute',
                 'Privilege': 'call,all',
                 'Channel': 'SIP/pcm_dev-0000000b',
                 'Uniqueid': '1338379282.18',
                 'Meetme': '800',
                 'Usernum': '1',
                 'Status': 'off'}

        manager = Mock(service_manager.MeetmeServiceManager)
        service_manager.manager = manager

        service_manager.parse_meetmemute(event)

        manager.unmute.assert_called_once_with('800', 1)

    def test_publish_change(self):
        service_notifier.notifier = Mock(service_notifier.MeetmeServiceNotifier)

        manager = service_manager.MeetmeServiceManager()
        manager._cache = {'test': 'status'}

        manager._publish_change()

        service_notifier.notifier.publish_meetme_update.assert_called_once_with(manager._cache)

    @patch('xivo_cti.dao.meetme_features_dao.muted_on_join_by_number', muted_on_join_by_number)
    @patch('time.time', my_time)
    @patch('xivo_cti.dao.linefeaturesdao.get_cid_for_channel', get_cid_for_channel)
    def test_join_originate(self):
        channel = 'SIP/kljfh-1234'
        join_time = 12345.654

        my_time.return_value = join_time
        find_by_confno.return_value = 2
        get_config.return_value = (conf_room_name, conf_room_number, True, 'default')
        muted_on_join_by_number.return_value = False
        get_cid_for_channel.return_value = ('"Tester 1" <1002>', 'Tester 1', '1002')

        self.manager._cache = {conf_room_number: {'number': conf_room_number,
                                                  'name': conf_room_name,
                                                  'pin_required': True,
                                                  'start_time': 0,
                                                  'members': {}}}

        self.manager.join(channel, conf_room_number, 1, conf_room_number, conf_room_number)

        expected = {conf_room_number: {'number': conf_room_number,
                                       'name': conf_room_name,
                                       'pin_required': True,
                                       'start_time': join_time,
                                       'members': {1: {'join_order': 1,
                                                       'join_time': join_time,
                                                       'number': '1002',
                                                       'name': 'Tester 1',
                                                       'channel': channel,
                                                       'muted': False}}}}

        self.assertEqual(self.manager._cache, expected)
