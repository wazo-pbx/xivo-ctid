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

import logging
import time

from xivo_bus.collectd.switchboard import (SwitchboardEnteredEvent,
                                           SwitchboardCompletedEvent,
                                           SwitchboardAbandonedEvent,
                                           SwitchboardForwardedEvent,
                                           SwitchboardTransferredEvent,
                                           SwitchboardWaitTimeEvent)
from xivo_bus.resources.calls.transfer import CompleteTransferEvent

from xivo_cti.ioc.context import context
from xivo_cti.database import statistics as statistic_dao


logger = logging.getLogger(__name__)


class InvalidCallException(Exception):
    pass


class State(object):

    unknown, ringing, on_hold, answered, completed, abandoned, transferred, forwarded = (
        'unknown', 'ringing', 'on_hold', 'answered', 'completed', 'abandoned', 'transferred', 'forwarded',
    )


class Call(object):

    def __init__(self):
        self.state = State.unknown
        self.start_time = time.time()
        self.answer_time = None
        self.end_time = None
        self.hold_duration = 0
        self.hold_time = None

    def __eq__(self, other):
        return (isinstance(other, self.__class__)
                and self.state == other.state
                and self.start_time == other.start_time
                and self.answer_time == other.answer_time
                and self.end_time == other.end_time
                and self.hold_duration == other.hold_duration)

    def __ne__(self, other):
        return not self.__eq__(other)

    def on_abandon(self):
        if self.state == State.on_hold:
            self.hold_duration += time.time() - self.hold_time

        self.state = State.abandoned
        self.end_time = time.time()

    def on_answer(self):
        if self.state == State.ringing:
            self.state = State.answered
            self.answer_time = time.time()

    def on_end(self):
        if not self.end_time:
            self.end_time = time.time()

        if self.state == State.answered:
            self.state = State.completed
        elif self.state == State.on_hold:
            self.state = State.abandoned

    def on_enter_queue(self):
        self.state = State.ringing

    def on_forward(self):
        self.end_time = time.time()
        self.state = State.forwarded

    def on_hold(self):
        if self.state == State.answered:
            self.state = State.on_hold
            self.hold_time = time.time()

    def on_resume(self):
        if not self.state == State.on_hold:
            return

        self.hold_duration += time.time() - self.hold_time
        self.hold_time = None
        self.state = State.answered

    def on_transfer(self):
        self.state = State.transferred
        self.end_time = time.time()

    def wait_time(self):
        if not self.start_time:
            return 0
        elif not self.answer_time:
            return self.end_time - self.start_time
        else:
            return self.answer_time - self.start_time + self.hold_duration


class Dispatcher(object):

    def __init__(self, switchboard_queues, factory=None):
        factory = factory or self._switchboard_factory
        self._switchboards = {name: factory(name) for name in switchboard_queues}
        self._switchboard_by_linked_id = {}
        self._hold_transfer = set()
        self._transfer_recipients = set()
        self._transfer_id_to_linked_id = {}

    def on_hold_called(self, transfer_id):
        self._hold_transfer.add(transfer_id)

    def on_transfer_id_added(self, event):
        transfer_id = event.get('Value')
        linked_id = event['Uniqueid']

        if linked_id not in self._transfer_recipients:
            return

        if transfer_id in self._hold_transfer:
            self._transfer_id_to_linked_id[transfer_id] = linked_id

        self._transfer_recipients.remove(linked_id)

    def on_transfer_role(self, event):
        if event['Value'] == 'recipient':
            self._transfer_recipients.add(event['Uniqueid'])

    def on_call_abandon(self, linked_id):
        switchboard = self._switchboard_by_linked_id.get(linked_id)
        if not switchboard:
            return

        switchboard.on_abandon(linked_id)

    def on_call_answer(self, linked_id):
        switchboard = self._switchboard_by_linked_id.get(linked_id)
        if not switchboard:
            return

        switchboard.on_answer(linked_id)

    def on_call_end(self, linked_id):
        switchboard = self._switchboard_by_linked_id.pop(linked_id, None)
        if not switchboard:
            return

        switchboard.on_call_end(linked_id)

    def on_call_forward(self, linked_id):
        switchboard = self._switchboard_by_linked_id.pop(linked_id, None)
        if not switchboard:
            return

        switchboard.on_call_forward(linked_id)

    def on_hold_call(self, linked_id):
        switchboard = self._switchboard_by_linked_id.get(linked_id)
        if not switchboard:
            return

        switchboard.on_hold_call(linked_id)

    def on_incoming_call(self, linked_id, queue):
        switchboard = self._switchboards.get(queue)
        if not switchboard:
            return

        switchboard.on_start(linked_id)
        self._switchboard_by_linked_id[linked_id] = switchboard

    def on_enter_queue(self, linked_id):
        switchboard = self._switchboard_by_linked_id.get(linked_id)
        if not switchboard:
            return

        switchboard.on_enter_queue(linked_id)

    def on_resume_call(self, linked_id):
        switchboard = self._switchboard_by_linked_id.get(linked_id)
        if not switchboard:
            return

        switchboard.on_resume_call(linked_id)

    def on_transfer(self, linked_id, transfer_id=None):
        switchboard = self._switchboard_by_linked_id.get(linked_id)
        if not switchboard:
            return

        if transfer_id not in self._hold_transfer:
            switchboard.on_transfer(linked_id)
            del self._switchboard_by_linked_id[linked_id]
        else:
            new_linked_id = self._transfer_id_to_linked_id.pop(transfer_id)
            if new_linked_id:
                self._rename(switchboard, linked_id, new_linked_id)
                self._switchboard_by_linked_id[new_linked_id] = switchboard
                self._hold_transfer.remove(transfer_id)
                switchboard.rename(linked_id, new_linked_id)
            switchboard.on_hold_call(linked_id)

    @staticmethod
    def _switchboard_factory(queue_name):
        return Switchboard(queue_name)


class BusParser(object):

    def __init__(self, bus_listener, task_queue, switchboard_statistic_dispatcher):
        self._bus_listener = bus_listener
        self._task_queue = task_queue
        self._dispatcher = switchboard_statistic_dispatcher

    def register_callbacks(self):
        self._bus_listener.add_callback(CompleteTransferEvent.routing_key, self.on_transfer_completed)

    def on_transfer_completed(self, body, msg):
        if body['name'] != 'transfer_completed':
            return

        linked_id = body['data']['transferred_call']
        transfer_id = body['data']['id']
        self._task_queue.put(self._dispatcher.on_transfer, linked_id, transfer_id)


class AMIParser(object):

    _attended_transfer = u'ATTENDEDTRANSFER'
    _linked_id_end = u'LINKEDID_END'
    _forward_events = [u'FULL', u'JOINEMPTY', u'LEAVEEMPTY', u'DIVERT_CA_RATIO', u'DIVERT_HOLDTIME']

    def __init__(self, switchboard_queues, switchboard_hold_queues, switchboard_statistic_dispatcher):
        self._switchboard_queues = switchboard_queues
        self._switchboard_hold_queues = switchboard_hold_queues
        self._switchboard_or_hold_queues = switchboard_queues + switchboard_hold_queues
        self._dispatcher = switchboard_statistic_dispatcher

    def on_bridge_enter(self, event):
        linked_id = event.get(u'Linkedid')
        if not linked_id:
            return

        self._dispatcher.on_call_answer(linked_id)

    def on_cel(self, event):
        cel_event = event.get(u'EventName')
        linked_id = event.get(u'LinkedID')
        if not linked_id:
            return

        if cel_event == self._linked_id_end:
            self._dispatcher.on_call_end(linked_id)
        elif cel_event == self._attended_transfer:
            self._dispatcher.on_transfer(linked_id)

    def on_queue_caller_abandon(self, event):
        linked_id = event.get(u'Linkedid')
        queue = event.get(u'Queue')
        if not linked_id or queue not in self._switchboard_or_hold_queues:
            return

        self._dispatcher.on_call_abandon(linked_id)

    def on_queue_caller_leave(self, event):
        unique_id = event.get(u'Uniqueid')
        queue = event.get(u'Queue')
        if not unique_id or queue not in self._switchboard_hold_queues:
            return

        self._dispatcher.on_resume_call(unique_id)

    def on_queue_caller_join(self, event):
        linked_id = event.get(u'Linkedid')
        if not linked_id:
            return

        queue = event.get(u'Queue')
        if queue in self._switchboard_queues:
            self._dispatcher.on_enter_queue(linked_id)
        elif queue in self._switchboard_hold_queues:
            self._dispatcher.on_hold_call(linked_id)

    def on_set_var(self, event):
        linked_id = event.get(u'Linkedid')
        variable = event.get(u'Variable')
        value = event.get(u'Value')
        if not linked_id:
            return

        if variable == 'XIVO_QUEUENAME' and value in self._switchboard_queues:
            self._dispatcher.on_incoming_call(linked_id, value)
        elif value and variable == u'BLINDTRANSFER':
            self._dispatcher.on_transfer(linked_id)
        elif variable == u'XIVO_QUEUELOG_EVENT' and value in self._forward_events:
            self._dispatcher.on_call_forward(linked_id)
        elif variable == u'XIVO_FWD_TYPE' and value == u'QUEUE_NOANSWER':
            self._dispatcher.on_call_forward(linked_id)
        elif variable == u'XIVO_TRANSFER_ID':
            self._dispatcher.on_transfer_id_added(event)
        elif variable == u'XIVO_TRANSFER_ROLE':
            self._dispatcher.on_transfer_role(event)


class Publisher(object):

    _state_to_msg_map = {State.abandoned: SwitchboardAbandonedEvent,
                         State.completed: SwitchboardCompletedEvent,
                         State.transferred: SwitchboardTransferredEvent,
                         State.forwarded: SwitchboardForwardedEvent}

    def __init__(self, collectd_publisher, queue_name):
        self._collectd_publisher = collectd_publisher
        self._queue_name = queue_name

    def publish_call_events(self, call):
        self._publish_collectd_events(call)
        self._insert_call_events(call)

    def _insert_call_events(self, call):
        statistic_dao.insert_switchboard_call(call.start_time, call.state, call.wait_time(), self._queue_name)

    def _publish_collectd_events(self, call):
        events = [self._get_call_start_event(call),
                  self._get_call_end_event(call),
                  self._get_wait_time(call)]

        if None in events:
            raise InvalidCallException

        [self._publish(msg) for msg in events]

    def _publish(self, msg):
        self._collectd_publisher.publish(msg)

    def _get_call_start_event(self, call):
        return SwitchboardEnteredEvent(self._queue_name, call.start_time)

    def _get_call_end_event(self, call):
        Klass = self._state_to_msg_map.get(call.state)
        if Klass:
            return Klass(self._queue_name, call.end_time)

    def _get_wait_time(self, call):
        return SwitchboardWaitTimeEvent(self._queue_name, call.wait_time())


class Switchboard(object):

    def __init__(self, queue_name, publisher=None):
        self._calls = {}
        if publisher:
            self._publisher = publisher
        else:
            self._publisher = Publisher(context.get('collectd_publisher'), queue_name)

    def rename(self, old, new):
        call = self._calls.pop(old, None)
        if not call:
            return

        self._calls[new] = call

    def on_abandon(self, linked_id):
        call = self._calls.get(linked_id)
        if not call:
            return

        call.on_abandon()
        # _call_completed is not called because its going to be forwarded if on timeout

    def on_answer(self, linked_id):
        call = self._calls.get(linked_id)
        if not call:
            return

        call.on_answer()

    def on_call_end(self, linked_id):
        call = self._calls.get(linked_id)
        if not call:
            return

        call.on_end()
        self._call_completed(linked_id)

    def on_call_forward(self, linked_id):
        call = self._calls.get(linked_id)
        if not call:
            call = self._calls[linked_id] = Call()

        call.on_forward()
        self._call_completed(linked_id)

    def on_enter_queue(self, linked_id):
        call = self._calls.get(linked_id)
        if not call:
            return

        call.on_enter_queue()

    def on_hold_call(self, linked_id):
        call = self._calls.get(linked_id)
        if not call:
            return

        call.on_hold()

    def on_resume_call(self, linked_id):
        call = self._calls.get(linked_id)
        if not call:
            return

        call.on_resume()

    def on_start(self, linked_id):
        self._calls[linked_id] = Call()

    def on_transfer(self, linked_id):
        call = self._calls.get(linked_id)
        if not call:
            return

        call.on_transfer()
        self._call_completed(linked_id)

    def _call_completed(self, linked_id):
        call = self._calls.pop(linked_id, None)
        if not call:
            return

        try:
            self._publisher.publish_call_events(call)
        except InvalidCallException:
            logger.info('invalid call cannot publish stats %s', linked_id)
