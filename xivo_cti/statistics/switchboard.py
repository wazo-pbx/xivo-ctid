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

from xivo_cti.ioc.context import context


logger = logging.getLogger(__name__)


class CallEvents(object):

    def __init__(self):
        self.start_time = time.time()
        self.is_abandoned = False
        self.is_transfered = False
        self.answer_time = None
        self.end_time = None
        self.hold_duration = 0
        self.hold_time = None

    def __eq__(self, other):
        return (isinstance(other, self.__class__)
                and self.is_abandoned == other.is_abandoned
                and self.is_transfered == other.is_transfered
                and self.start_time == other.start_time
                and self.answer_time == other.answer_time
                and self.end_time == other.end_time
                and self.hold_duration == other.hold_duration)

    def __ne__(self, other):
        return not self.__eq__(other)

    def on_abandon(self):
        t = time.time()
        self.is_abandoned = True
        self.end_time = t
        if self.hold_time:
            self.hold_duration += t - self.hold_time
            self.hold_time = None

    def on_answer(self):
        if not self.answer_time:
            self.answer_time = time.time()

    def on_end(self):
        if not self.end_time:
            self.end_time = time.time()

    def on_hold(self):
        if not self.hold_time:
            self.hold_time = time.time()

    def on_resume(self):
        if not self.hold_time:
            return

        self.hold_duration += time.time() - self.hold_time
        self.hold_time = None

    def on_transfer(self):
        if not self.end_time:
            self.end_time = time.time()
            self.is_transfered = True

    @property
    def is_answered(self):
        if not self.answer_time:
            return False
        else:
            return not self.is_abandoned and not self.is_transfered

    def wait_time(self):
        if not self.answer_time:
            return self.end_time - self.start_time
        else:
            return self.answer_time - self.start_time + self.hold_duration


class Dispatcher(object):

    def __init__(self, switchboard_queues, factory=None):
        factory = factory or self._switchboard_factory
        self._switchboards = {name: factory(name) for name in switchboard_queues}
        self._switchboard_by_linked_id = {}

    def on_call_abandon(self, linked_id):
        switchboard = self._switchboard_by_linked_id.pop(linked_id, None)
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

    def on_hold_call(self, linked_id):
        switchboard = self._switchboard_by_linked_id.get(linked_id)
        if not switchboard:
            return

        switchboard.on_hold_call(linked_id)

    def on_new_call(self, queue, linked_id):
        switchboard = self._switchboards.get(queue)
        if not switchboard:
            return

        self._switchboard_by_linked_id[linked_id] = switchboard
        switchboard.on_new_call(linked_id)

    def on_resume_call(self, linked_id):
        switchboard = self._switchboard_by_linked_id.get(linked_id)
        if not switchboard:
            return

        switchboard.on_resume_call(linked_id)

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
            self._dispatcher.on_new_call(queue, linked_id)
        elif queue in self._switchboard_hold_queues:
            self._dispatcher.on_hold_call(linked_id)

    def on_set_var(self, event):
        linked_id = event.get(u'Linkedid')
        variable = event.get(u'Variable')
        if not linked_id or variable != 'BLINDTRANSFER':
            return

        self._dispatcher.on_transfer(linked_id)


class Publisher(object):

    _application = 'callcontrol'

    def __init__(self, collectd_publisher, queue_name):
        self._collectd_publisher = collectd_publisher
        self._queue_name = queue_name

    def publish_call_events(self, linked_id, call_events):
        [self._publish(msg) for msg in [self._publish_call_start(linked_id, call_events),
                                        self._publish_call_answered(linked_id, call_events),
                                        self._publish_call_abandoned(linked_id, call_events),
                                        self._publish_call_transfered(linked_id, call_events),
                                        self._publish_wait_time(linked_id, call_events)]]

    def _publish(self, msg):
        if msg:
            self._collectd_publisher.publish(msg)

    def _publish_call_abandoned(self, linked_id, call_events):
        if not call_events.is_abandoned:
            return

        logger.debug('%s: abandoned', linked_id)

    def _publish_call_answered(self, linked_id, call_events):
        if not call_events.is_answered:
            return

        logger.debug('%s: answered', linked_id)

    def _publish_call_transfered(self, linked_id, call_events):
        if not call_events.is_transfered:
            return

        logger.debug('%s: transfered', linked_id)

    def _publish_call_start(self, linked_id, call_events):
        logger.debug('%s: new call', linked_id)

    def _publish_wait_time(self, linked_id, call_events):
        logger.debug('%s:, wait time %s', linked_id, call_events.wait_time())


class Switchboard(object):

    def __init__(self, queue_name, publisher=None):
        self._call_events = {}
        if publisher:
            self._publisher = publisher
        else:
            self._publisher = Publisher(context.get('collectd_publisher'), queue_name)

    def on_abandon(self, linked_id):
        events = self._call_events.get(linked_id)
        if not events:
            return

        events.on_abandon()
        self._call_completed(linked_id)

    def on_answer(self, linked_id):
        events = self._call_events.get(linked_id)
        if not events:
            return

        events.on_answer()

    def on_call_end(self, linked_id):
        events = self._call_events.get(linked_id)
        if not events:
            return

        events.on_end()
        self._call_completed(linked_id)

    def on_new_call(self, linked_id):
        self._call_events[linked_id] = CallEvents()

    def on_hold_call(self, linked_id):
        events = self._call_events.get(linked_id)
        if not events:
            return

        events.on_hold()

    def on_resume_call(self, linked_id):
        events = self._call_events.get(linked_id)
        if not events:
            return

        events.on_resume()

    def on_transfer(self, linked_id):
        events = self._call_events.get(linked_id)
        if not events:
            return

        events.on_transfer()
        self._call_completed(linked_id)

    def _call_completed(self, linked_id):
        events = self._call_events.pop(linked_id, None)
        if not events:
            return

        self._publisher.publish_call_events(linked_id, events)
