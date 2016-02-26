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

from ..switchboard import CallEvents, Dispatcher, Parser, Publisher, Switchboard

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


class TestDispatcher(unittest.TestCase):

    def setUp(self):
        switchboard_queues = [SWITCHBOARD_QUEUE, 'other_sb']
        self._default_switchboard = Mock(Switchboard)
        self._other_switchboard = Mock(Switchboard)

        self.dispatcher = Dispatcher(switchboard_queues, self._new_switchboard)

    def test_on_bridge_enter_when_not_a_switchboard(self):
        self.dispatcher.on_new_call('foobar', s.linked_id)

        self.assert_not_called(self._default_switchboard.on_new_call)
        self.assert_not_called(self._other_switchboard.on_new_call)

    def test_on_bridge_enter_on_a_switchboard(self):
        self.dispatcher.on_new_call('other_sb', s.linked_id)

        self.assert_not_called(self._default_switchboard.on_new_call)
        self._other_switchboard.on_new_call.assert_called_once_with(s.linked_id)

    def test_on_call_abandon(self):
        self.dispatcher.on_new_call(SWITCHBOARD_QUEUE, s.linked_id)

        self.dispatcher.on_call_abandon(s.linked_id)

        self.assert_not_called(self._other_switchboard.on_abandon)
        self._default_switchboard.on_abandon.assert_called_once_with(s.linked_id)

    def test_on_call_answer_not_a_switchboard(self):
        self.dispatcher.on_new_call('foobar', s.linked_id)

        self.dispatcher.on_call_answer(s.linked_id)

        self.assert_not_called(self._default_switchboard.on_answer)
        self.assert_not_called(self._other_switchboard.on_answer)

    def test_on_call_answer_on_a_switchboard(self):
        self.dispatcher.on_new_call(SWITCHBOARD_QUEUE, s.linked_id)

        self.dispatcher.on_call_answer(s.linked_id)

        self.assert_not_called(self._other_switchboard.on_answer)
        self._default_switchboard.on_answer.assert_called_once_with(s.linked_id)

    def test_on_call_end_not_a_switchboard(self):
        self.dispatcher.on_new_call('foobar', s.linked_id)

        self.dispatcher.on_call_end(s.linked_id)

        self.assert_not_called(self._default_switchboard.on_call_end)
        self.assert_not_called(self._other_switchboard.on_call_end)

    def test_on_call_end_on_a_switchboard(self):
        self.dispatcher.on_new_call(SWITCHBOARD_QUEUE, s.linked_id)

        self.dispatcher.on_call_end(s.linked_id)

        self.assert_not_called(self._other_switchboard.on_call_end)
        self._default_switchboard.on_call_end.assert_called_once_with(s.linked_id)

    def test_on_hold_call(self):
        self.dispatcher.on_new_call(SWITCHBOARD_QUEUE, s.linked_id)

        self.dispatcher.on_hold_call(s.linked_id)

        self.assert_not_called(self._other_switchboard.on_hold_call)
        self._default_switchboard.on_hold_call.assert_called_once_with(s.linked_id)

    def test_on_resume_call(self):
        self.dispatcher.on_new_call(SWITCHBOARD_QUEUE, s.linked_id)

        self.dispatcher.on_resume_call(s.linked_id)

        self.assert_not_called(self._other_switchboard.on_resume_call)
        self._default_switchboard.on_resume_call.assert_called_once_with(s.linked_id)

    def test_on_transfer_not_a_switchboard(self):
        self.dispatcher.on_new_call(SWITCHBOARD_QUEUE, s.linked_id)

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

        assert_that(self.dispatcher.on_call_abandon.call_count, equal_to(0))

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

        self.dispatcher.on_new_call.assert_called_once_with(SWITCHBOARD_QUEUE,
                                                            LINKED_ID)

    def test_on_queue_caller_join_not_switchboard_queue(self):
        self.parser.on_queue_caller_join(HOLD_EVENT)

        assert_that(self.dispatcher.on_new_call.call_count, equal_to(0))

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


class TestSwitchboard(unittest.TestCase):

    def setUp(self):
        self.publisher = Mock(Publisher)
        self.switchboard = Switchboard('foobar', self.publisher)

    def test_call_abandoned_in_the_switchboard_queue(self):
        t1 = time.time()
        t2 = t1 + 23

        self.at(partial(self.switchboard.on_new_call, s.linked_id), t1)
        self.at(partial(self.switchboard.on_abandon, s.linked_id), t2)

        expected = self.new_call_events(t1, None, t2, abandoned=True)

        self.publisher.publish_call_events.assert_called_once_with(s.linked_id, expected)

    def test_call_abandoned_in_the_switchboard_hold_queue(self):
        t1 = time.time()
        t2 = t1 + 23
        t3 = t2 + 120
        t4 = t3 + 200

        self.at(partial(self.switchboard.on_new_call, s.linked_id), t1)
        self.at(partial(self.switchboard.on_answer, s.linked_id), t2)
        self.at(partial(self.switchboard.on_hold_call, s.linked_id), t3)
        self.at(partial(self.switchboard.on_abandon, s.linked_id), t4)

        expected = self.new_call_events(t1, t2, t4, abandoned=True, hold_time=t3)

        self.publisher.publish_call_events.assert_called_once_with(s.linked_id, expected)

    def test_call_completed_by_the_operator(self):
        t1 = time.time()
        t2 = t1 + 23
        t3 = t2 + 180

        self.at(partial(self.switchboard.on_new_call, s.linked_id), t1)
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

        self.at(partial(self.switchboard.on_new_call, s.linked_id), t1)
        self.at(partial(self.switchboard.on_answer, s.linked_id), t2)
        self.at(partial(self.switchboard.on_hold_call, s.linked_id), t3)
        self.at(partial(self.switchboard.on_resume_call, s.linked_id), t4)
        self.at(partial(self.switchboard.on_call_end, s.linked_id), t5)

        expected = self.new_call_events(t1, t2, t5, hold_time=t3, resume_time=t4)

        self.publisher.publish_call_events.assert_called_once_with(s.linked_id, expected)

    def test_transfered_calls(self):
        t1 = time.time()
        t2 = t1 + 23
        t3 = t2 + 180

        self.at(partial(self.switchboard.on_new_call, s.linked_id), t1)
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

        self.at(partial(self.switchboard.on_new_call, s.linked_id), t1)
        self.at(partial(self.switchboard.on_answer, s.linked_id), t2)
        self.at(partial(self.switchboard.on_hold_call, s.linked_id), t3)
        self.at(partial(self.switchboard.on_resume_call, s.linked_id), t4)
        self.at(partial(self.switchboard.on_transfer, s.linked_id), t5)

        expected = self.new_call_events(t1, t2, t5, transfered=True, hold_time=t3, resume_time=t4)

        self.publisher.publish_call_events.assert_called_once_with(s.linked_id, expected)

    def at(self, f, t):
        with patch('xivo_cti.statistics.switchboard.time.time', return_value=t):
            f()

    def new_call_events(self, new_time, answer_time, end_time, transfered=False,
                        abandoned=False, hold_time=None, resume_time=None):
        with patch('xivo_cti.statistics.switchboard.time.time') as time:
            time.return_value = new_time

            call_events = CallEvents()

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
            else:
                call_events.on_end()

        return call_events
