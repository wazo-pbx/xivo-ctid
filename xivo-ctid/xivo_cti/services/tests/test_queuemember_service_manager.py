#!/usr/bin/python
# vim: set fileencoding=utf-8 :

# Copyright (C) 2007-2012  Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Pro-formatique SARL. See the LICENSE file at top of the
# source tree or delivered in the installable package in which XiVO CTI Server
# is distributed for more details.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import unittest

from tests.mock import Mock, call, ANY, patch
from xivo_dao.helpers import queuemember_formatter
from xivo_cti.services.queuemember_service_manager import QueueMemberServiceManager
from xivo_cti.tools.delta_computer import DictDelta, DeltaComputer
from xivo_cti.services.queuemember_service_notifier import QueueMemberServiceNotifier
from xivo_cti.dao.innerdatadao import InnerdataDAO


LINE_IDENTITY = 'sip/i7vbu0'
USER_INTERFACE = u'SIP/i7vbu0'
AGENT_INTERFACE = u'Agent/3001'
AGENT_NUMBER = '3001'
GROUP_NAME = 'group'
QUEUE_NAME = 'file'


class TestQueueMemberServiceManager(unittest.TestCase):

    def setUp(self):
        self.queuemember_service_manager = QueueMemberServiceManager()
        self.queuemember_service_notifier = Mock(QueueMemberServiceNotifier)
        self.queuemember_service_manager.queuemember_notifier = self.queuemember_service_notifier

        self.old_queuemember_formatter = queuemember_formatter.QueueMemberFormatter
        queuemember_formatter.QueueMemberFormatter = Mock()

        self.ami_event = {
            'Queue': 'queue1',
            'Location': 'location1',
            'Status': 'status1',
            'Paused': 'yes',
            'Membership': 'dynamic',
            'CallsTaken': '0',
            'Penalty': '0',
            'LastCall': 'none'}

        self.A = {
            'queue_name': 'queueA',
            'interface': 'agentA',
            'penalty': 0}
        self.keyA = 'agentA,queueA'
        self.tupleA = ('agentA', 'queueA')
        self.B = {
            'queue_name': 'queueB',
            'interface': 'agentB',
            'penalty': 1}
        self.keyB = 'agentB,queueB'
        self.tupleB = ('agentB', 'queueB')
        self.C = {
            'queue_name': 'queueC',
            'interface': 'agentC',
            'penalty': 2}
        self.keyC = 'agentC,queueC'
        self.tupleC = ('agentC', 'queueC')
        self.D = {
            'queue_name': 'queueD',
            'interface': 'agentD',
            'penalty': 2}
        self.keyD = 'agentD,queueD'
        self.tupleD = ('agentD', 'queueD')

    def tearDown(self):
        queuemember_formatter.QueueMemberFormatter = self.old_queuemember_formatter

    def test_update_config_add(self):
        queuemember_dao = Mock()
        queuemember_dao.get_queuemembers = Mock()
        queuemember_dao.get_queuemembers.return_value = {self.keyA: self.A,
                                                         self.keyB: self.B,
                                                         self.keyC: self.C}
        self.queuemember_service_manager.queuemember_dao = queuemember_dao
        innerdata_dao = Mock()
        innerdata_dao.get_queuemembers_static = Mock()
        innerdata_dao.get_queuemembers_static.return_value = {}
        self.queuemember_service_manager.innerdata_dao = innerdata_dao
        self.queuemember_service_manager.delta_computer = DeltaComputer()
        expected_ami_request = [self.tupleA, self.tupleB, self.tupleC]
        expected_removed = DictDelta({}, {}, {})

        self.queuemember_service_manager.update_config()

        self.queuemember_service_notifier.queuemember_config_updated.assert_called_once_with(expected_removed)
        self.queuemember_service_notifier.request_queuemembers_to_ami.assert_called_once_with(expected_ami_request)

    def test_add_dynamic_queuemember(self):
        queuemember_formatted = {'location1,queue1': {'queue_name': 'queue1',
                                                      'interface': 'location1'}
                                 }
        queuemember_formatter.QueueMemberFormatter.format_queuemember_from_ami_add.return_value = queuemember_formatted
        expected_delta = DictDelta(queuemember_formatted, {}, {})

        self.queuemember_service_manager.add_dynamic_queuemember(self.ami_event)

        queuemember_formatter.QueueMemberFormatter.format_queuemember_from_ami_add.assert_called_with(self.ami_event)
        self.queuemember_service_notifier.queuemember_config_updated.assert_called_with(expected_delta)

    def test_remove_dynamic_queuemember(self):
        queuemembers_to_remove = {'Agent/2345,service': {'queue_name': 'service', 'interface': 'Agent/2345'},
                                  'Agent/2309,service': {'queue_name': 'service', 'interface': 'Agent/2309'}}

        queuemember_formatter.QueueMemberFormatter.format_queuemember_from_ami_remove.return_value = queuemembers_to_remove

        self.queuemember_service_manager.remove_dynamic_queuemember(self.ami_event)

        queuemember_formatter.QueueMemberFormatter.format_queuemember_from_ami_remove.assert_called_with(self.ami_event)
        self.queuemember_service_notifier.queuemember_config_updated.assert_called_with(DictDelta({}, {}, queuemembers_to_remove))

    def test_update_queuemember(self):
        ami_event = self.ami_event
        self.queuemember_service_manager.innerdata_dao = Mock()
        self.queuemember_service_manager.delta_computer = Mock()

        self.queuemember_service_manager.update_one_queuemember(ami_event)

        innerdata_dao_method_calls = self.queuemember_service_manager.innerdata_dao.method_calls
        delta_computer_method_calls = self.queuemember_service_manager.delta_computer.method_calls
        notifier_method_calls = self.queuemember_service_manager.queuemember_notifier.method_calls
        self.assertTrue(innerdata_dao_method_calls == [call.get_queuemembers_config()])
        self.assertTrue(delta_computer_method_calls == [call.compute_delta_no_delete(ANY, ANY)])
        self.assertTrue(notifier_method_calls == [call.queuemember_config_updated(ANY)])

    def test_get_queuemember_to_request_empty(self):
        delta = DictDelta({}, {}, {})
        expected_result = []

        result = self.queuemember_service_manager._get_queuemembers_to_request(delta)

        self.assertEqual(result, expected_result)

    def test_get_queuemember_to_request_full(self):
        delta = DictDelta(
            {
                self.keyA: self.A,
                self.keyB: self.B
            },
            {
                self.keyC: {'penalty': '0'}
            },
            {self.keyD: self.D})
        expected_result = [self.tupleA,
                           self.tupleB,
                           self.tupleC]
        innerdata_dao_get = Mock()
        innerdata_dao_get.return_value = self.C
        self.queuemember_service_manager.innerdata_dao = Mock()
        self.queuemember_service_manager.innerdata_dao.get_queuemember = innerdata_dao_get

        result = self.queuemember_service_manager._get_queuemembers_to_request(delta)

        self.assertEqual(result, expected_result)

    def test_get_queuemember_to_remove_empty(self):
        delta = DictDelta({}, {}, {})
        expected_result = DictDelta({}, {}, {})

        result = self.queuemember_service_manager._get_queuemembers_to_remove(delta)

        self.assertEqual(result, expected_result)

    def test_get_queuemember_to_remove_full(self):
        delta = DictDelta(
            {self.keyA: self.A},
            {self.keyB: {'penalty': '0'}},
            {
                self.keyC: self.C,
                self.keyD: self.D
            })
        expected_result = DictDelta({}, {}, {self.keyC: self.C,
                                             self.keyD: self.D})

        result = self.queuemember_service_manager._get_queuemembers_to_remove(delta)

        self.assertEqual(result, expected_result)

    def test_toggle_pause(self):
        queuemember_formatted = {'agent1,queue1': {'queue_name': 'queue1',
                                                   'interface': 'agent1',
                                                   'paused': 'yes'}}

        self.queuemember_service_manager.queuemember_notifier = Mock()
        queuemember_formatter.QueueMemberFormatter.format_queuemember_from_ami_pause.return_value = queuemember_formatted

        self.queuemember_service_manager.toggle_pause(self.ami_event)

        queuemember_formatter.QueueMemberFormatter.format_queuemember_from_ami_pause.assert_called_once_with(self.ami_event)
        self.queuemember_service_manager.queuemember_notifier.queuemember_config_updated.assert_called_once_with(
            DictDelta(add={},
                      change=queuemember_formatted,
                      delete={}))

    @patch('xivo_dao.queue_features_dao.get_queue_name', Mock(return_value=QUEUE_NAME))
    @patch('xivo_cti.dao.userfeaturesdao.get_line_identity', Mock(return_value=LINE_IDENTITY))
    @patch('xivo_cti.dao.userfeaturesdao.get_agent_number', Mock(return_value=AGENT_NUMBER))
    def test_is_queue_member_user_member(self):
        user_id = 1
        queue_id = 2
        queue_members = {'%s,%s' % (USER_INTERFACE, QUEUE_NAME): {'interface': USER_INTERFACE,
                                                                  'membership': u'static',
                                                                  'paused': u'0',
                                                                  'penalty': u'0',
                                                                  'queue_name': u'file',
                                                                  'status': u'1'}}
        innerdata_dao = Mock(InnerdataDAO)
        innerdata_dao.get_queuemembers_config.return_value = queue_members

        self.queuemember_service_manager.innerdata_dao = innerdata_dao

        result = self.queuemember_service_manager.is_queue_member(user_id, queue_id)

        self.assertTrue(result)

    @patch('xivo_dao.queue_features_dao.get_queue_name', Mock(return_value=QUEUE_NAME))
    @patch('xivo_cti.dao.userfeaturesdao.get_line_identity', Mock(return_value=LINE_IDENTITY))
    @patch('xivo_cti.dao.userfeaturesdao.get_agent_number', Mock(return_value=AGENT_NUMBER))
    def test_is_queue_member_agent(self):
        user_id = 1
        queue_id = 2
        queue_members = {'%s,%s' % (AGENT_INTERFACE, QUEUE_NAME): {'interface': AGENT_INTERFACE,
                                                                   'membership': u'static',
                                                                   'paused': u'0',
                                                                   'penalty': u'0',
                                                                   'queue_name': u'file',
                                                                   'status': u'1'}}

        innerdata_dao = Mock(InnerdataDAO)
        innerdata_dao.get_queuemembers_config.return_value = queue_members

        self.queuemember_service_manager.innerdata_dao = innerdata_dao

        result = self.queuemember_service_manager.is_queue_member(user_id, queue_id)

        self.assertTrue(result)

    @patch('xivo_dao.group_dao.get_name', Mock(return_value=GROUP_NAME))
    @patch('xivo_cti.dao.userfeaturesdao.get_line_identity', Mock(return_value=LINE_IDENTITY))
    def test_is_group_member_user_member(self):
        user_id = 1
        group_id = 2
        queue_members = {'%s,%s' % (USER_INTERFACE, GROUP_NAME): {'interface': USER_INTERFACE,
                                                                  'membership': u'static',
                                                                  'paused': u'0',
                                                                  'penalty': u'0',
                                                                  'queue_name': u'file',
                                                                  'status': u'1'}}

        innerdata_dao = Mock(InnerdataDAO)
        innerdata_dao.get_queuemembers_config.return_value = queue_members

        self.queuemember_service_manager.innerdata_dao = innerdata_dao

        result = self.queuemember_service_manager.is_group_member(user_id, group_id)

        self.assertTrue(result)
