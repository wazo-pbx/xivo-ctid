# -*- coding: utf-8 -*-

# Copyright (C) 2013-2014 Avencall
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
from datetime import datetime
from mock import Mock, patch
from xivo_cti.services.queue_member.member import QueueMemberState, QueueMember


class TestQueueMember(unittest.TestCase):

    @patch('xivo_cti.services.queue_member.common.format_queue_member_id')
    def test_id_on_initialisation(self, mock_format_queue_member_id):
        queue_name = 'queue1'
        member_name = 'Agent/1234'
        mock_format_queue_member_id.return_value = 'something'

        queue_member = QueueMember(queue_name, member_name, None)

        mock_format_queue_member_id.assert_called_once_with(queue_name, member_name)
        self.assertEqual(queue_member.id, 'something')

    @patch('xivo_cti.services.queue_member.common.is_agent_member_name')
    def test_is_agent(self, mock_is_agent_member_name):
        queue_name = 'queue1'
        member_name = 'Agent/1234'
        mock_is_agent_member_name.return_value = True

        queue_member = QueueMember(queue_name, member_name, None)
        result = queue_member.is_agent()

        mock_is_agent_member_name.assert_called_once_with(member_name)
        self.assertEqual(result, True)

    def test_to_cti_config(self):
        queue_name = 'queue1'
        member_name = 'Agent/1234'
        state = Mock()

        queue_member = QueueMember(queue_name, member_name, state)
        result = queue_member.to_cti_config()

        expected_result = {
            'queue_name': queue_name,
            'interface': member_name,
            'membership': 'static'
        }
        self.assertEqual(result, expected_result)
        state._to_cti.assert_called_once_with(expected_result)

    def test_to_cti_status(self):
        queue_name = 'queue1'
        member_name = 'Agent/1234'
        state = Mock()

        queue_member = QueueMember(queue_name, member_name, state)
        result = queue_member.to_cti_status()

        expected_result = {
            'queue_name': queue_name,
            'interface': member_name,
            'membership': 'static'
        }
        self.assertEqual(result, expected_result)
        state._to_cti.assert_called_once_with(expected_result)


class TestQueueMemberState(unittest.TestCase):

    def test_copy(self):
        state1 = QueueMemberState()
        state1.calls_taken = 42

        state2 = state1.copy()
        state2.interface = 'Local/423232@foobar'

        self.assertEqual(state1.calls_taken, state2.calls_taken)
        self.assertNotEqual(state1.interface, state2.interface)
        self.assertTrue(state1.__dict__ is not state2.__dict__)

    def test_equal(self):
        state1 = QueueMemberState()
        state2 = QueueMemberState()

        self.assertEqual(state1, state2)

    def test_not_equal(self):
        state1 = QueueMemberState()
        state1.calls_taken += 1
        state2 = QueueMemberState()

        self.assertNotEqual(state1, state2)

    def test_from_dao_queue_member(self):
        dao_queue_member = Mock()
        dao_queue_member.penalty = 1
        expected_state = QueueMemberState()
        expected_state.penalty = 1

        state = QueueMemberState.from_dao_queue_member(dao_queue_member)

        self.assertEqual(state, expected_state)

    def test_from_ami_queue_member(self):
        ami_event = {
            'Queue': 'foobar',
            'Name': 'Agent/2',
            'Location': 'SIP/abcdef',
            'Membership': 'dynamic',
            'Penalty': '1',
            'CallsTaken': '42',
            'LastCall': '1355154813',
            'Status': '1',
            'Paused': '1',
            'Skills': 'agent-17',
        }
        expected_state = QueueMemberState()
        expected_state.calls_taken = 42
        expected_state.interface = 'SIP/abcdef'
        expected_state.last_call = datetime.fromtimestamp(1355154813)
        expected_state.paused = True
        expected_state.penalty = 1
        expected_state.status = '1'

        state = QueueMemberState.from_ami_queue_member(ami_event)

        self.assertEqual(state, expected_state)

    def test_from_ami_queue_member_status(self):
        ami_event = {
            'Queue': 'foobar',
            'Location': 'SIP/abcdef',
            'MemberName': 'Agent/2',
            'Membership': 'dynamic',
            'Penalty': '1',
            'CallsTaken': '42',
            'LastCall': '1355154813',
            'Status': '1',
            'Paused': '1',
            'Skills': 'agent-17',
        }
        expected_state = QueueMemberState()
        expected_state.calls_taken = 42
        expected_state.interface = 'SIP/abcdef'
        expected_state.last_call = datetime.fromtimestamp(1355154813)
        expected_state.paused = True
        expected_state.penalty = 1
        expected_state.status = '1'

        state = QueueMemberState.from_ami_queue_member_status(ami_event)

        self.assertEqual(state, expected_state)

    def test_from_ami_queue_member_added(self):
        ami_event = {
            'Queue': 'foobar',
            'Location': 'SIP/abcdef',
            'MemberName': 'Agent/2',
            'Membership': 'dynamic',
            'Penalty': '1',
            'CallsTaken': '42',
            'LastCall': '1355154813',
            'Status': '1',
            'Paused': '1',
        }
        expected_state = QueueMemberState()
        expected_state.calls_taken = 42
        expected_state.interface = 'SIP/abcdef'
        expected_state.last_call = datetime.fromtimestamp(1355154813)
        expected_state.paused = True
        expected_state.penalty = 1
        expected_state.status = '1'

        state = QueueMemberState.from_ami_queue_member_added(ami_event)

        self.assertEqual(state, expected_state)

    def test_to_cti(self):
        state = QueueMemberState()
        state.status = '123'
        result = {}
        expected_result = {
            'callstaken': '0',
            'paused': '0',
            'penalty': '0',
            'status': '123',
            'lastcall': '',
        }

        state._to_cti(result)

        self.assertEqual(result, expected_result)
