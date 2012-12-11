# -*- coding: UTF-8 -*-

import unittest
from datetime import datetime
from mock import Mock
from xivo_cti.services.queue_members.member import QueueMemberState


class TestQueueMemberState(unittest.TestCase):

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
