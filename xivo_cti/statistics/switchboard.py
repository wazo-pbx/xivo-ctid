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

from xivo_bus.collectd.calls.event import (CallAbandonedCollectdEvent,
                                           CallConnectCollectdEvent,
                                           CallDurationCollectdEvent,
                                           CallEndCollectdEvent,
                                           CallStartCollectdEvent)
from xivo_cti.ioc.context import context


logger = logging.getLogger(__name__)


class CallEvents(object):

    def __init__(self):
        self.start_time = time.time()
        self.answer_time = None
        self.end_time = None

    def __eq__(self, other):
        return (isinstance(other, self.__class__)
                and self.start_time == other.start_time
                and self.answer_time == other.answer_time
                and self.end_time == other.end_time)

    def __ne__(self, other):
        return not self.__eq__(other)

    def on_answer(self):
        if not self.answer_time:
            self.answer_time = time.time()

    def on_end(self):
        self.end_time = time.time()


class Dispatcher(object):

    def __init__(self, switchboard_queues, factory=None):
        factory = factory or self._switchboard_factory
        self._switchboards = {name: factory(name) for name in switchboard_queues}
        self._switchboard_by_linked_id = {}

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

    def on_new_call(self, queue, linked_id):
        switchboard = self._switchboards.get(queue)
        if not switchboard:
            return

        self._switchboard_by_linked_id[linked_id] = switchboard
        switchboard.on_new_call(linked_id)

    def on_transfer(self, linked_id):
        switchboard = self._switchboard_by_linked_id.pop(linked_id, None)
        if not switchboard:
            return

        switchboard.on_transfer(linked_id)

    @staticmethod
    def _switchboard_factory(queue_name):
        return Switchboard(queue_name)


class Parser(object):

    _attended_transfer = u'ATTENDEDTRANSFER'
    _linked_id_end = u'LINKEDID_END'

    def __init__(self, switchboard_statistic_dispatcher):
        self._dispatcher = switchboard_statistic_dispatcher

    def on_bridge_enter(self, event):
        linked_id = event.get(u'Linkedid')
        if linked_id:
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

    def on_queue_caller_join(self, event):
        queue = event.get(u'Queue')
        linked_id = event.get(u'Linkedid')
        if queue and linked_id:
            self._dispatcher.on_new_call(queue, linked_id)

    def on_set_var(self, event):
        if event.get('Variable') != 'BLINDTRANSFER':
            return

        linked_id = event.get(u'Linkedid')
        if linked_id:
            self._dispatcher.on_transfer(linked_id)


class Publisher(object):

    _application = 'callcontrol'

    def __init__(self, collectd_publisher, queue_name):
        self._collectd_publisher = collectd_publisher
        self._queue_name = queue_name

    def publish_call_events(self, linked_id, call_events):
        [self._publish(msg) for msg in [self._publish_call_start(linked_id, call_events),
                                        self._publish_call_connected(linked_id, call_events),
                                        self._publish_call_abandoned(linked_id, call_events),
                                        self._publish_call_end(linked_id, call_events),
                                        self._publish_call_duration(linked_id, call_events)]]

    def _publish(self, msg):
        if msg:
            self._collectd_publisher.publish(msg)

    def _publish_call_abandoned(self, linked_id, call_events):
        if not self._is_call_abandoned(call_events):
            return

        return CallAbandonedCollectdEvent(self._application, self._queue_name, time=call_events.end_time)

    def _publish_call_connected(self, linked_id, call_events):
        if self._is_call_abandoned(call_events):
            return

        return CallConnectCollectdEvent(self._application, self._queue_name, time=call_events.answer_time)

    def _publish_call_duration(self, linked_id, call_events):
        duration = call_events.end_time - call_events.start_time
        return CallDurationCollectdEvent(self._application, self._queue_name, duration)

    def _publish_call_end(self, linked_id, call_events):
        if self._is_call_abandoned(call_events):
            return

        return CallEndCollectdEvent(self._application, self._queue_name, time=call_events.end_time)

    def _publish_call_start(self, linked_id, call_events):
        return CallStartCollectdEvent(self._application, self._queue_name, time=call_events.start_time)

    @staticmethod
    def _is_call_abandoned(call_events):
        return call_events.answer_time is None


class Switchboard(object):

    def __init__(self, queue_name, publisher=None):
        self._call_events = {}
        if publisher:
            self._publisher = publisher
        else:
            self._publisher = Publisher(context.get('collectd_publisher'), queue_name)

    def on_answer(self, linked_id):
        events = self._call_events.get(linked_id)
        if not events:
            return

        events.on_answer()

    def on_call_end(self, linked_id):
        self._call_completed(linked_id)

    def on_new_call(self, linked_id):
        self._call_events[linked_id] = CallEvents()

    def on_transfer(self, linked_id):
        self._call_completed(linked_id)

    def _call_completed(self, linked_id):
        events = self._call_events.pop(linked_id, None)
        if not events:
            return

        events.on_end()
        self._publisher.publish_call_events(linked_id, events)
