# -*- coding: utf-8 -*-

# Copyright (C) 2016 Avencall
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

import time
import unittest

from functools import partial
from hamcrest import assert_that, equal_to
from mock import Mock, patch, sentinel as s

from ..switchboard import Call, Dispatcher, Parser, Publisher, Switchboard

LINKED_ID = u'1456240331.88'
SWITCHBOARD_QUEUE = u'__switchboard'
SWITCHBOARD_HOLD_QUEUE = u'__switchboard_hold'
QUEUE_CALLER_JOIN_EVENT = {u'Linkedid': LINKED_ID,
                           u'Queue': SWITCHBOARD_QUEUE,
                           u'Uniqueid': LINKED_ID,
                           u'Event': u'QueueCallerJoin'}
BRIDGE_ENTER_EVENT = {u'Linkedid': LINKED_ID,
                      u'Event': u'BridgeEnter'}
LINKEDID_END_EVENT = {u'LinkedID': LINKED_ID,
                      u'EventName': u'LINKEDID_END',
                      u'Event': u'CEL'}
BLIND_TRANSFER_EVENT = {u'Linkedid': LINKED_ID,
                        u'Value': u'true',
                        u'Uniqueid': u'1456414620.302',
                        u'Variable': u'BLINDTRANSFER',
                        u'Event': u'VarSet'}
ATTENDED_TRANSFER_EVENT = {u'LinkedID': LINKED_ID,
                           u'EventName': u'ATTENDEDTRANSFER',
                           u'UniqueID': u'1456413895.274',
                           u'Event': u'CEL'}
HOLD_EVENT = {u'Linkedid': LINKED_ID,
              u'Queue': SWITCHBOARD_HOLD_QUEUE,
              u'Uniqueid': u'1456418880.4',
              u'Event': u'QueueCallerJoin'}
RESUME_EVENT = {u'Queue': SWITCHBOARD_HOLD_QUEUE,
                u'Ast11Uniqueid': u'1456418880.4',
                u'Uniqueid': LINKED_ID,
                u'Event': u'QueueCallerLeave'}
ABANDON_EVENT = {u'Linkedid': LINKED_ID,
                 u'Queue': SWITCHBOARD_HOLD_QUEUE,
                 u'Uniqueid': u'1456419086.18',
                 u'Event': u'QueueCallerAbandon'}
FULL_EVENT = {u'Linkedid': LINKED_ID,
              u'Value': u'FULL',
              u'Uniqueid': u'1456494965.270',
              u'Variable': u'XIVO_QUEUELOG_EVENT',
              u'Event': u'VarSet'}
CLOSED_EVENT = {u'Linkedid': LINKED_ID,
                u'Value': u'CLOSED',
                u'Uniqueid': u'1456497821.279',
                u'Variable': u'XIVO_QUEUELOG_EVENT',
                u'Event': u'VarSet'}
JOIN_EMPTY_EVENT = {u'Linkedid': LINKED_ID,
                    u'Value': u'JOINEMPTY',
                    u'Uniqueid': u'1456497821.279',
                    u'Variable': u'XIVO_QUEUELOG_EVENT',
                    u'Event': u'VarSet'}
LEAVE_EMPTY_EVENT = {u'Linkedid': LINKED_ID,
                     u'Value': u'LEAVEEMPTY',
                     u'Uniqueid': u'1456497821.279',
                     u'Variable': u'XIVO_QUEUELOG_EVENT',
                     u'Event': u'VarSet'}
DIVERT_HOLDTIME_EVENT = {u'Linkedid': LINKED_ID,
                         u'Value': u'DIVERT_HOLDTIME',
                         u'Uniqueid': u'1456497821.279',
                         u'Variable': u'XIVO_QUEUELOG_EVENT',
                         u'Event': u'VarSet'}
DIVERT_CA_RATIO_EVENT = {u'Linkedid': LINKED_ID,
                         u'Value': u'DIVERT_CA_RATIO',
                         u'Uniqueid': u'1456497821.279',
                         u'Variable': u'XIVO_QUEUELOG_EVENT',
                         u'Event': u'VarSet'}
TIMEOUT_EVENT = {u'Linkedid': LINKED_ID,
                 u'Value': u'QUEUE_NOANSWER',
                 u'Uniqueid': u'1456494379.259',
                 u'Variable': u'XIVO_FWD_TYPE',
                 u'Event': u'VarSet'}
INCOMING_CALL_EVENT = {u'Linkedid': LINKED_ID,
                       u'Value': u'__switchboard',
                       u'Uniqueid': u'1456503648.356',
                       u'Variable': u'XIVO_QUEUENAME',
                       u'Event': u'VarSet'}


def queue_called(queue_name):
    def wrapped(f):
        def dec(*args, **kwargs):
            instance = args[0]
            instance.dispatcher.on_incoming_call(s.linked_id, queue_name)
            return f(*args, **kwargs)
        return dec
    return wrapped


class TestDispatcher(unittest.TestCase):

    def setUp(self):
        switchboard_queues = [SWITCHBOARD_QUEUE, 'other_sb']
        self._default_switchboard = Mock(Switchboard)
        self._other_switchboard = Mock(Switchboard)

        self.dispatcher = Dispatcher(switchboard_queues, self._new_switchboard)

    @queue_called('foobar')
    def test_on_enter_queue_when_not_a_switchboard(self):
        self.dispatcher.on_enter_queue(s.linked_id)

        self.assert_not_called(self._default_switchboard.on_enter_queue)
        self.assert_not_called(self._other_switchboard.on_enter_queue)

    @queue_called('other_sb')
    def test_on_bridge_enter_on_a_switchboard(self):
        self.dispatcher.on_enter_queue(s.linked_id)

        self.assert_not_called(self._default_switchboard.on_new_call)
        self._other_switchboard.on_new_call.assert_called_once_with(s.linked_id)

    @queue_called(SWITCHBOARD_QUEUE)
    def test_on_call_abandon(self):
        self.dispatcher.on_call_abandon(s.linked_id)

        self.assert_not_called(self._other_switchboard.on_abandon)
        self._default_switchboard.on_abandon.assert_called_once_with(s.linked_id)

    @queue_called('foobar')
    def test_on_call_answer_not_a_switchboard(self):
        self.dispatcher.on_call_answer(s.linked_id)

        self.assert_not_called(self._default_switchboard.on_answer)
        self.assert_not_called(self._other_switchboard.on_answer)

    @queue_called(SWITCHBOARD_QUEUE)
    def test_on_call_answer_on_a_switchboard(self):
        self.dispatcher.on_call_answer(s.linked_id)

        self.assert_not_called(self._other_switchboard.on_answer)
        self._default_switchboard.on_answer.assert_called_once_with(s.linked_id)

    @queue_called('foobar')
    def test_on_call_end_not_a_switchboard(self):
        self.dispatcher.on_call_end(s.linked_id)

        self.assert_not_called(self._default_switchboard.on_call_end)
        self.assert_not_called(self._other_switchboard.on_call_end)

    @queue_called(SWITCHBOARD_QUEUE)
    def test_on_call_end_on_a_switchboard(self):
        self.dispatcher.on_call_end(s.linked_id)

        self.assert_not_called(self._other_switchboard.on_call_end)
        self._default_switchboard.on_call_end.assert_called_once_with(s.linked_id)

    @queue_called(SWITCHBOARD_QUEUE)
    def test_on_call_forward(self):
        self.dispatcher.on_call_forward(s.linked_id)

        self.assert_not_called(self._other_switchboard.on_call_forward)
        self._default_switchboard.on_call_forward.assert_called_once_with(s.linked_id)

    @queue_called(SWITCHBOARD_QUEUE)
    def test_on_hold_call(self):
        self.dispatcher.on_hold_call(s.linked_id)

        self.assert_not_called(self._other_switchboard.on_hold_call)
        self._default_switchboard.on_hold_call.assert_called_once_with(s.linked_id)

    @queue_called(SWITCHBOARD_QUEUE)
    def test_on_resume_call(self):
        self.dispatcher.on_resume_call(s.linked_id)

        self.assert_not_called(self._other_switchboard.on_resume_call)
        self._default_switchboard.on_resume_call.assert_called_once_with(s.linked_id)

    @queue_called(SWITCHBOARD_QUEUE)
    def test_on_transfer_not_a_switchboard(self):
        self.dispatcher.on_transfer(s.linked_id)

        self.assert_not_called(self._other_switchboard.on_transfer)
        self._default_switchboard.on_transfer.assert_called_once_with(s.linked_id)

    def assert_not_called(self, mocked_fn):
        assert_that(mocked_fn.call_count, equal_to(0),
                    'expected no calls got {}'.format(mocked_fn.call_args_list))

    def _new_switchboard(self, name):
        if name == SWITCHBOARD_QUEUE:
            return self._default_switchboard
        else:
            return self._other_switchboard


class TestParser(unittest.TestCase):

    def setUp(self):
        self.dispatcher = Mock(Dispatcher)
        self.parser = Parser([SWITCHBOARD_QUEUE], [SWITCHBOARD_HOLD_QUEUE], self.dispatcher)

    def test_on_queue_caller_abandon_switchboard_hold_queue(self):
        self.parser.on_queue_caller_abandon(ABANDON_EVENT)

        self.dispatcher.on_call_abandon.assert_called_once_with(LINKED_ID)

    def test_on_queue_caller_abandon_switchboard_queue(self):
        event = dict(ABANDON_EVENT)
        event[u'Queue'] = SWITCHBOARD_QUEUE
        self.parser.on_queue_caller_abandon(event)

        self.dispatcher.on_call_abandon.assert_called_once_with(LINKED_ID)

    def test_on_queue_caller_abandon_other_queue(self):
        event = dict(ABANDON_EVENT)
        event[u'Queue'] = 'foobar'
        self.parser.on_queue_caller_abandon(event)

        assert_that(self.dispatcher.on_enter_queue.call_count, equal_to(0))

    def test_on_queue_caller_leave_hold_queues(self):
        self.parser.on_queue_caller_leave(RESUME_EVENT)

        self.dispatcher.on_resume_call.assert_called_once_with(LINKED_ID)

    def test_on_queue_caller_leave_not_hold_queues(self):
        event = dict(RESUME_EVENT)
        event[u'Queue'] = 'foobar'
        self.parser.on_queue_caller_leave(event)

        assert_that(self.dispatcher.on_resume_call.call_count, equal_to(0))

    def test_on_queue_caller_join_switchboard_queue(self):
        self.parser.on_queue_caller_join(QUEUE_CALLER_JOIN_EVENT)

        self.dispatcher.on_enter_queue.assert_called_once_with(LINKED_ID)

    def test_on_queue_caller_join_not_switchboard_queue(self):
        self.parser.on_queue_caller_join(HOLD_EVENT)

        assert_that(self.dispatcher.on_enter_queue.call_count, equal_to(0))

    def test_on_queue_caller_join_hold_queue(self):
        self.parser.on_queue_caller_join(HOLD_EVENT)

        self.dispatcher.on_hold_call.assert_called_once_with(LINKED_ID)

    def test_on_queue_caller_join_not_hold_queue(self):
        self.parser.on_queue_caller_join(QUEUE_CALLER_JOIN_EVENT)

        assert_that(self.dispatcher.on_hold_call.call_count, equal_to(0))

    def test_on_bridge_enter(self):
        self.parser.on_bridge_enter(BRIDGE_ENTER_EVENT)

        self.dispatcher.on_call_answer.assert_called_once_with(LINKED_ID)

    def test_on_cel_linked_id_end(self):
        self.parser.on_cel(LINKEDID_END_EVENT)

        self.dispatcher.on_call_end.assert_called_once_with(LINKED_ID)

    def test_on_cel_attended_transfer(self):
        self.parser.on_cel(ATTENDED_TRANSFER_EVENT)

        self.dispatcher.on_transfer.assert_called_once_with(LINKED_ID)

    def test_on_setvar_blind_transfer(self):
        self.parser.on_set_var(BLIND_TRANSFER_EVENT)

        self.dispatcher.on_transfer.assert_called_once_with(LINKED_ID)

    def test_on_setvar_closed_nothing_happens(self):
        self.parser.on_set_var(CLOSED_EVENT)

        assert_that(self.dispatcher.on_call_forward.call_count, equal_to(0))

    def test_on_setvar_divert_ca_ratio(self):
        self.parser.on_set_var(DIVERT_CA_RATIO_EVENT)

        self.dispatcher.on_call_forward.assert_called_once_with(LINKED_ID)

    def test_on_setvar_divert_hold_time(self):
        self.parser.on_set_var(DIVERT_HOLDTIME_EVENT)

        self.dispatcher.on_call_forward.assert_called_once_with(LINKED_ID)

    def test_on_setvar_full(self):
        self.parser.on_set_var(FULL_EVENT)

        self.dispatcher.on_call_forward.assert_called_once_with(LINKED_ID)

    def test_on_setvar_join_empty(self):
        self.parser.on_set_var(JOIN_EMPTY_EVENT)

        self.dispatcher.on_call_forward.assert_called_once_with(LINKED_ID)

    def test_on_setvar_leave_empty(self):
        self.parser.on_set_var(LEAVE_EMPTY_EVENT)

        self.dispatcher.on_call_forward.assert_called_once_with(LINKED_ID)

    def test_on_setvar_timeout(self):
        self.parser.on_set_var(TIMEOUT_EVENT)

        self.dispatcher.on_call_forward.assert_called_once_with(LINKED_ID)

    def test_on_setvat_queue_name(self):
        self.parser.on_set_var(INCOMING_CALL_EVENT)

        self.dispatcher.on_incoming_call.assert_called_once_with(LINKED_ID, SWITCHBOARD_QUEUE)


class TestSwitchboard(unittest.TestCase):

    def setUp(self):
        self.publisher = Mock(Publisher)
        self.switchboard = Switchboard('foobar', self.publisher)

    def test_call_abandoned_in_the_switchboard_queue(self):
        t1 = time.time()
        t2 = t1 + 23
        t3 = t2 + 1

        self.at(partial(self.switchboard.on_start, s.linked_id), t1)
        self.at(partial(self.switchboard.on_enter_queue, s.linked_id), t1)
        self.at(partial(self.switchboard.on_abandon, s.linked_id), t2)
        self.at(partial(self.switchboard.on_call_end, s.linked_id), t3)

        expected = self.new_call_events(t1, None, t2, abandoned=True)

        self.publisher.publish_call_events.assert_called_once_with(s.linked_id, expected)

    def test_call_abandoned_in_the_switchboard_hold_queue(self):
        t1 = time.time()
        t2 = t1 + 23
        t3 = t2 + 120
        t4 = t3 + 200
        t5 = t4 + 25

        self.at(partial(self.switchboard.on_start, s.linked_id), t1)
        self.at(partial(self.switchboard.on_enter_queue, s.linked_id), t1)
        self.at(partial(self.switchboard.on_answer, s.linked_id), t2)
        self.at(partial(self.switchboard.on_hold_call, s.linked_id), t3)
        self.at(partial(self.switchboard.on_abandon, s.linked_id), t4)
        self.at(partial(self.switchboard.on_call_end, s.linked_id), t5)

        expected = self.new_call_events(t1, t2, t4, abandoned=True, hold_time=t3)

        self.publisher.publish_call_events.assert_called_once_with(s.linked_id, expected)

    def test_call_completed_by_the_operator(self):
        t1 = time.time()
        t2 = t1 + 23
        t3 = t2 + 180

        self.at(partial(self.switchboard.on_start, s.linked_id), t1)
        self.at(partial(self.switchboard.on_enter_queue, s.linked_id), t1)
        self.at(partial(self.switchboard.on_answer, s.linked_id), t2)
        self.at(partial(self.switchboard.on_call_end, s.linked_id), t3)

        expected = self.new_call_events(t1, t2, t3)

        self.publisher.publish_call_events.assert_called_once_with(s.linked_id, expected)

    def test_call_completed_by_the_operator_after_hold(self):
        t1 = time.time()
        t2 = t1 + 23
        t3 = t2 + 180
        t4 = t3 + 10
        t5 = t4 + 21

        self.at(partial(self.switchboard.on_start, s.linked_id), t1)
        self.at(partial(self.switchboard.on_enter_queue, s.linked_id), t1)
        self.at(partial(self.switchboard.on_answer, s.linked_id), t2)
        self.at(partial(self.switchboard.on_hold_call, s.linked_id), t3)
        self.at(partial(self.switchboard.on_resume_call, s.linked_id), t4)
        self.at(partial(self.switchboard.on_call_end, s.linked_id), t5)

        expected = self.new_call_events(t1, t2, t5, hold_time=t3, resume_time=t4)

        self.publisher.publish_call_events.assert_called_once_with(s.linked_id, expected)

    def test_forwarded(self):
        t1 = time.time()
        t2 = t1 + 25

        self.at(partial(self.switchboard.on_start, s.linked_id), t1)
        self.at(partial(self.switchboard.on_call_forward, s.linked_id), t2)

        expected = self.new_call_events(t1, None, t2, forwarded=True)

        self.publisher.publish_call_events.assert_called_once_with(s.linked_id, expected)

    def test_transfered_calls(self):
        t1 = time.time()
        t2 = t1 + 23
        t3 = t2 + 180

        self.at(partial(self.switchboard.on_start, s.linked_id), t1)
        self.at(partial(self.switchboard.on_enter_queue, s.linked_id), t1)
        self.at(partial(self.switchboard.on_answer, s.linked_id), t2)
        self.at(partial(self.switchboard.on_transfer, s.linked_id), t3)

        expected = self.new_call_events(t1, t2, t3, transfered=True)

        self.publisher.publish_call_events.assert_called_once_with(s.linked_id, expected)

    def test_call_transfered_after_hold(self):
        t1 = time.time()
        t2 = t1 + 23
        t3 = t2 + 180
        t4 = t3 + 42
        t5 = t4 + 10

        self.at(partial(self.switchboard.on_start, s.linked_id), t1)
        self.at(partial(self.switchboard.on_enter_queue, s.linked_id), t1)
        self.at(partial(self.switchboard.on_answer, s.linked_id), t2)
        self.at(partial(self.switchboard.on_hold_call, s.linked_id), t3)
        self.at(partial(self.switchboard.on_resume_call, s.linked_id), t4)
        self.at(partial(self.switchboard.on_transfer, s.linked_id), t5)

        expected = self.new_call_events(t1, t2, t5, transfered=True, hold_time=t3, resume_time=t4)

        self.publisher.publish_call_events.assert_called_once_with(s.linked_id, expected)

    def test_full_queue(self):
        t1 = time.time()

        self.at(partial(self.switchboard.on_start, s.linked_id), t1)
        self.at(partial(self.switchboard.on_call_forward, s.linked_id), t1)

        expected = self.new_call_events(t1, None, t1, forwarded=True)

        self.publisher.publish_call_events.assert_called_once_with(s.linked_id, expected)

    def at(self, f, t):
        with patch('xivo_cti.statistics.switchboard.time.time', return_value=t):
            f()

    def new_call_events(self, new_time, answer_time, end_time, transfered=False,
                        abandoned=False, hold_time=None, resume_time=None, forwarded=False):
        with patch('xivo_cti.statistics.switchboard.time.time') as time:
            time.return_value = new_time

            call_events = Call()
            call_events.on_enter_queue()

            if answer_time:
                time.return_value = answer_time
                call_events.on_answer()

            if hold_time:
                time.return_value = hold_time
                call_events.on_hold()

            if resume_time:
                time.return_value = resume_time
                call_events.on_resume()

            time.return_value = end_time
            if abandoned:
                call_events.on_abandon()
            elif transfered:
                call_events.on_transfer()
            elif forwarded:
                call_events.on_forward()
            else:
                call_events.on_end()

        return call_events
