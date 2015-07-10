#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (C) 2012-2015 Avencall
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

import unittest
import copy
import time

from mock import Mock, NonCallableMock
from mock import patch
from xivo_cti.ioc.context import context
from xivo_cti.services.meetme import service_manager
from xivo_cti.services.meetme.service_manager import MeetmeServiceManager
from xivo_cti.services.meetme.service_notifier import MeetmeServiceNotifier
from xivo_cti import xivo_ami
from xivo_cti import dao
from xivo_cti.dao import user_dao
from xivo_cti.dao import meetme_dao

conf_room_number = '800'
conf_room_name = 'test_conf'


class TestMeetmeServiceManager(unittest.TestCase):

    def setUp(self):
        self.mock_notifier = NonCallableMock(MeetmeServiceNotifier)
        self.ami_class = Mock(xivo_ami.AMIClass)
        self.manager = service_manager.MeetmeServiceManager(
            self.mock_notifier,
            self.ami_class,
        )
        self.mock_manager = NonCallableMock(MeetmeServiceManager)
        context.register('meetme_service_notifier', self.mock_notifier)
        context.register('meetme_service_manager', self.mock_manager)

    def tearDown(self):
        context.reset()

    def test_invite(self):
        inviter_id = 5
        invitee_xid = 'user:xivo/3'
        invitee_interface = 'SIP/abcdef'
        meetme_context = 'myctx'
        meetme_number = '4003'
        meetme_caller_id = '"Conference My conf" <4003>'

        dao.user = Mock(user_dao.UserDAO)
        dao.meetme = Mock(meetme_dao.MeetmeDAO)
        dao.user.get_line_identity.return_value = invitee_interface
        dao.meetme.get_caller_id_from_context_number.return_value = meetme_caller_id
        self.manager._find_meetme_by_line = Mock(return_value=(meetme_context, meetme_number))

        response = self.manager.invite(inviter_id, invitee_xid)

        expected_return = 'message', {'message': 'Command sent succesfully'}

        self.assertEqual(response, expected_return)
        self.ami_class.sendcommand.assert_called_once_with(
            'Originate',
            [('Channel', invitee_interface),
             ('Context', meetme_context),
             ('Exten', meetme_number),
             ('Priority', '1'),
             ('Async', 'true'),
             ('CallerID', meetme_caller_id)]
        )

    def test_find_meetme_by_line(self):
        number = '4000'
        context = 'myctx'
        line_interface = 'SCCP/1234'
        channel = '%s-24734893' % line_interface

        self.manager._cache = {number: {'number': number,
                                        'name': 'my-conf-name',
                                        'pin_required': False,
                                        'start_time': time.time(),
                                        'context': context,
                                        'members': {1: {'join_order': 1,
                                                        'join_time': time.time() - 5,
                                                        'number': '1002',
                                                        'name': 'Tester 1',
                                                        'channel': channel,
                                                        'muted': False}}}}

        self.assertRaises(LookupError, self.manager._find_meetme_by_line, 'SIP/not-there')

        result_context, result_number = self.manager._find_meetme_by_line(line_interface)

        self.assertEqual(result_context, context)
        self.assertEqual(result_number, number)

    @patch('xivo_dao.meetme_dao.is_a_meetme', Mock(return_value=True))
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
                 'User': '1',
                 'CallerIDNum': caller_id_number,
                 'CallerIDName': caller_id_name,
                 'ConnectedLineNum': '<unknown>',
                 'ConnectedLineName': '<unknown>'}

        service_manager.parse_join(event)

        self.mock_manager.join.assert_called_once_with(channel,
                                                       number,
                                                       1,
                                                       caller_id_name,
                                                       caller_id_number)

    @patch('xivo_dao.meetme_dao.is_a_meetme', Mock(return_value=False))
    def test_parse_join_paging(self):
        channel = 'SIP/i7vbu0-00000001'
        number = '8834759845'
        caller_id_name = 'Père Noël'
        caller_id_number = '1000'
        event = {'Event': 'MeetmeJoin',
                 'Privilege': 'call,all',
                 'Channel': channel,
                 'Uniqueid': '1338219287.2',
                 'Meetme': number,
                 'User': '1',
                 'CallerIDNum': caller_id_number,
                 'CallerIDName': caller_id_name,
                 'ConnectedLineNum': '<unknown>',
                 'ConnectedLineName': '<unknown>'}

        service_manager.parse_join(event)

        self.assertEqual(self.mock_manager.join.call_count, 0)

    @patch('xivo_dao.meetme_dao.get_config', Mock(return_value=(conf_room_name, conf_room_number, True, 'default')))
    @patch('xivo_dao.meetme_dao.find_by_confno', Mock(return_value=5))
    @patch('xivo_dao.meetme_dao.muted_on_join_by_number', Mock(return_value=True))
    @patch('time.time')
    def test_join(self, mock_time):
        start = 12345.123
        channel = 'SIP/mon_trunk-1234'

        mock_time.return_value = start

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

        self.mock_notifier.publish_meetme_update.assert_called_once_with(expected)

    @patch('xivo_dao.meetme_dao.get_config', Mock(return_value=(conf_room_name, conf_room_number, True, 'test')))
    @patch('xivo_dao.meetme_dao.find_by_confno', Mock(return_value=4))
    @patch('xivo_dao.meetme_dao.muted_on_join_by_number', Mock(return_value=True))
    @patch('time.time')
    def test_join_second(self, mock_time):
        start_time = 12345678.123
        join_time = 12345699.123
        phone_number = '4185551234'
        channel = 'SIP/pcm_dev-0000005d'

        mock_time.return_value = start_time

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

        mock_time.return_value = join_time
        self.manager.join(channel, conf_room_number, 2, phone_number, phone_number)

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

        self.mock_notifier.publish_meetme_update.assert_called_once_with(expected)

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

    @patch('time.time')
    def test_build_joining_member_status(self, mock_time):
        channel = 'SIP/kjsdfh-12356'
        join_time = 1234.1234
        mock_time.return_value = join_time
        result = service_manager._build_joining_member_status(1, 'Tester One', '666', channel, False)
        expected = {'join_order': 1,
                    'join_time': join_time,
                    'number': '666',
                    'name': 'Tester One',
                    'channel': channel,
                    'muted': False}

        self.assertEqual(result, expected)

    @patch('xivo_dao.meetme_dao.get_config', Mock(return_value=(conf_room_name, conf_room_number, True, 'my_context')))
    @patch('xivo_dao.meetme_dao.find_by_confno', Mock(return_value=2))
    def test_set_room_config(self):
        self.manager._set_room_config(conf_room_number)

        result = self.manager._cache

        expected = {conf_room_number: {'name': conf_room_name,
                                       'number': conf_room_number,
                                       'pin_required': True,
                                       'start_time': 0,
                                       'context': 'my_context',
                                       'members': {}}}

        self.assertEqual(result, expected)

    @patch('xivo_dao.meetme_dao.is_a_meetme', Mock(return_value=True))
    def test_parse_leave(self):
        event = {'Event': 'MeetmeLeave',
                 'Privilege': 'call,all',
                 'Channel': 'SIP/i7vbu0-00000000',
                 'Uniqueid': '1338219251.0',
                 'Meetme': '800',
                 'User': '1',
                 'CallerIDNum': '1000',
                 'CallerIDName': 'Père Noël',
                 'ConnectedLineNum': '<unknown>',
                 'ConnectedLineName': '<unknown>',
                 'Duration': '31'}

        service_manager.parse_leave(event)

        self.mock_manager.leave.assert_called_once_with('800', 1)

    @patch('xivo_dao.meetme_dao.is_a_meetme', Mock(return_value=False))
    def test_parse_leave_paging(self):
        event = {'Event': 'MeetmeLeave',
                 'Privilege': 'call,all',
                 'Channel': 'SIP/i7vbu0-00000000',
                 'Uniqueid': '1338219251.0',
                 'Meetme': '0834758704',
                 'User': '1',
                 'CallerIDNum': '1000',
                 'CallerIDName': 'Père Noël',
                 'ConnectedLineNum': '<unknown>',
                 'ConnectedLineName': '<unknown>',
                 'Duration': '31'}

        service_manager.parse_leave(event)

        self.assertEqual(self.mock_manager.leave.call_count, 0)

    def test_leave(self):
        start_time = 1234556.123

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

        self.manager.leave(conf_room_number, 1)

        expected = {conf_room_number: {'number': conf_room_number,
                                       'name': conf_room_name,
                                       'pin_required': True,
                                       'start_time': start_time,
                                       'members': {2: {'join_order': 2,
                                                       'join_time': start_time + 10,
                                                       'number': '4181235555',
                                                       'name': '4181235555',
                                                       'channel': 'DAHDI/i1/4181235555-5'}}}}

        self.mock_notifier.publish_meetme_update.assert_called_once_with(expected)
        self.mock_notifier.reset_mock()

        self.manager.leave(conf_room_number, 2)

        expected = {conf_room_number: {'number': conf_room_number,
                                       'name': conf_room_name,
                                       'pin_required': True,
                                       'start_time': 0,
                                       'members': {}}}

        self.mock_notifier.publish_meetme_update.assert_called_once_with(expected)

    def test_leave_after_restart(self):
        start_time = 1234556.123

        self.manager._cache = {
            conf_room_number: {
                'number': conf_room_number,
                'name': conf_room_name,
                'pin_required': True,
                'start_time': start_time,
                'members': {},
            }
        }

        self.manager.leave(conf_room_number, 1)

        self.assertEqual(self.mock_notifier.publish_meetme_update.call_count, 0)

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

    @patch('xivo_dao.meetme_dao.get_config', Mock(return_value=(conf_room_name, conf_room_number, True, 'default')))
    @patch('xivo_dao.meetme_dao.find_by_confno', Mock(return_value=2))
    @patch('xivo_dao.meetme_dao.muted_on_join_by_number', Mock(return_value=False))
    @patch('time.time')
    def test_join_when_empty(self, mock_time):
        channel = 'SIP/kljfh-1234'
        join_time = 12345.654

        mock_time.return_value = join_time

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

    @patch('xivo_dao.meetme_dao.get_configs')
    def test_initial_state(self, mock_get_configs):
        mock_get_configs.return_value = [('Conference1', '9000', True, 'default'),
                                         ('Conference2', '9001', False, 'test'),
                                         ('Conference3', '9002', False, 'test')]

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

        self.mock_notifier.publish_meetme_update.assert_called_once_with(expected)

    def test_add_room(self):
        self.manager._add_room('Conference1', '9000', True, 'ctx')

        expected = {'9000': {'number': '9000',
                             'name': 'Conference1',
                             'pin_required': True,
                             'start_time': 0,
                             'context': 'ctx',
                             'members': {}}}

        self.assertEqual(self.manager._cache, expected)

    @patch('xivo_dao.meetme_dao.get_configs')
    def test_initialize_configs_with_members(self, mock_get_configs):
        mock_get_configs.return_value = [('Conference2', '9001', False, 'test'),
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

    @patch('xivo_dao.meetme_dao.is_a_meetme', Mock(return_value=True))
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

        service_manager.parse_meetmelist(event)

        self.mock_manager.refresh.assert_called_once_with(channel, '800', 1, 'My Name', '666', False)

    @patch('xivo_dao.meetme_dao.is_a_meetme', Mock(return_value=False))
    def test_parse_meetmelist_paging(self):
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

        service_manager.parse_meetmelist(event)

        self.assertEqual(self.mock_manager.refresh.call_count, 0)

    @patch('xivo_dao.meetme_dao.get_config', Mock(return_value=(conf_room_name, conf_room_number, False, 'dev')))
    @patch('xivo_dao.meetme_dao.find_by_confno', Mock(return_value=1))
    def test_refresh_empty(self):
        channel = 'DAHDI/i1/5555555555-1'
        name = 'First Testeur'
        number = '5555555555'

        self.manager.refresh(channel, conf_room_number, 1, name, number, is_muted=True)

        expected = {conf_room_number: {'number': conf_room_number,
                                       'name': conf_room_name,
                                       'pin_required': False,
                                       'start_time': -1,
                                       'context': 'dev',
                                       'members': {1: {'join_order': 1,
                                                       'join_time': -1,
                                                       'number': number,
                                                       'name': name,
                                                       'channel': channel,
                                                       'muted': True}}}}

        self.mock_notifier.publish_meetme_update.assert_called_once_with(expected)

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
        self.manager.mute(conf_room_number, 1)
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

        self.mock_notifier.publish_meetme_update.assert_called_once_with(expected)

    def test_unmuting(self):
        self.manager.unmute(conf_room_number, 1)
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

        self.mock_notifier.publish_meetme_update.assert_called_once_with(expected)

    @patch('xivo_dao.meetme_dao.is_a_meetme', Mock(return_value=True))
    def test_parse_mute(self):
        event = {'Event': 'MeetmeMute',
                 'Privilege': 'call,all',
                 'Channel': 'SIP/pcm_dev-0000000b',
                 'Uniqueid': '1338379282.18',
                 'Meetme': '800',
                 'User': '1',
                 'Status': 'on'}

        service_manager.parse_meetmemute(event)

        self.mock_manager.mute.assert_called_once_with('800', 1)

    @patch('xivo_dao.meetme_dao.is_a_meetme', Mock(return_value=False))
    def test_parse_mute_paging(self):
        event = {'Event': 'MeetmeMute',
                 'Privilege': 'call,all',
                 'Channel': 'SIP/pcm_dev-0000000b',
                 'Uniqueid': '1338379282.18',
                 'Meetme': '800',
                 'User': '1',
                 'Status': 'on'}

        service_manager.parse_meetmemute(event)

        self.assertEquals(self.mock_manager.mute.call_count, 0)

    @patch('xivo_dao.meetme_dao.is_a_meetme', Mock(return_value=True))
    def test_parse_unmute(self):
        event = {'Event': 'MeetmeMute',
                 'Privilege': 'call,all',
                 'Channel': 'SIP/pcm_dev-0000000b',
                 'Uniqueid': '1338379282.18',
                 'Meetme': '800',
                 'User': '1',
                 'Status': 'off'}

        service_manager.parse_meetmemute(event)

        self.mock_manager.unmute.assert_called_once_with('800', 1)

    @patch('xivo_dao.meetme_dao.muted_on_join_by_number', Mock(return_value=False))
    @patch('xivo_dao.user_line_dao.get_cid_for_channel', Mock(return_value=('"Tester 1" <1002>', 'Tester 1', '1002')))
    @patch('time.time')
    def test_join_originate(self, mock_time):
        channel = 'SIP/kljfh-1234'
        join_time = 12345.654

        mock_time.return_value = join_time

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
