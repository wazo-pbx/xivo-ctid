# -*- coding: utf-8 -*-

# XiVO CTI Server
#
# Copyright (C) 2007-2012  Avencall
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

import logging
from collections import namedtuple
from xivo_cti.ami.ami_callback_handler import AMICallbackHandler
from xivo_cti.context import context
from xivo_cti.services.queue_service_manager import NotAQueueException
from xivo_cti import dao

logger = logging.getLogger("QueueStatisticsProducer")
QueueCounters = namedtuple('QueueCounters', ['available', 'EWT', 'Talking'])

LOGGEDAGENT_STATNAME = "Xivo-LoggedAgents"
AVAILABLEAGENT_STATNAME = "Xivo-AvailableAgents"
EWT_STATNAME = "Xivo-EWT"
TALKINGAGENT_STATNAME = "Xivo-TalkingAgents"


def register_events():
    callback_handler = AMICallbackHandler.get_instance()
    callback_handler.register_callback('QueueSummary', parse_queue_summary)


def parse_queue_summary(queuesummary_event):
    queue_name = queuesummary_event['Queue']
    counters = QueueCounters(available=queuesummary_event['Available'], EWT=queuesummary_event['HoldTime'], Talking=queuesummary_event['Talking'])

    queue_statistics_producer = context.get('queue_statistics_producer')
    queue_service_manager = context.get('queue_service_manager')
    try:
        queue_id = queue_service_manager.get_queue_id(queue_name)
        queue_statistics_producer.on_queue_summary(queue_id, counters)
    except NotAQueueException:
        pass


class QueueStatisticsProducer(object):

    def __init__(self, statistics_notifier):
        self.notifier = statistics_notifier
        self.dao = dao
        self.queues_of_agent = {}
        self.logged_agents = set()
        self.queues = set()

    def on_queue_added(self, queueid):
        self.queues.add(queueid)
        self._notify_change(queueid)

    def on_queue_removed(self, queueid):
        self.queues.remove(queueid)
        for queues_of_current_agent in self.queues_of_agent.itervalues():
            queues_of_current_agent.discard(queueid)

    def on_queue_member_added(self, queue_member):
        if queue_member.is_agent():
            queueid = self.dao.innerdata.get_queue_id(queue_member.queue_name)
            agentid = queue_member.member_name
            self._on_agent_added(queueid, agentid)

    def _on_agent_added(self, queueid, agentid):
        if agentid not in self.queues_of_agent:
            self.queues_of_agent[agentid] = set()
        self.queues_of_agent[agentid].add(queueid)
        self._notify_change(queueid)

    def on_queue_member_removed(self, queue_member):
        if queue_member.is_agent():
            queueid = self.dao.innerdata.get_queue_id(queue_member.queue_name)
            agentid = queue_member.member_name
            self._on_agent_removed(queueid, agentid)

    def _on_agent_removed(self, queueid, agentid):
        self.queues_of_agent[agentid].remove(queueid)
        if agentid in self.logged_agents:
            self._notify_change(queueid)
        logger.debug('agent id %s removed from queue id %s', agentid, queueid)

    def on_agent_loggedon(self, agentid):
        self.logged_agents.add(agentid)
        if agentid in self.queues_of_agent:
            for queueid in self.queues_of_agent[agentid]:
                self._notify_change(queueid)
        else:
            self.queues_of_agent[agentid] = set()

    def on_agent_loggedoff(self, agentid):
        self.logged_agents.discard(agentid)
        if agentid in self.queues_of_agent:
            for queueid in self.queues_of_agent[agentid]:
                self._notify_change(queueid)

    def on_queue_summary(self, queue_id, counters):
        message = {queue_id: {AVAILABLEAGENT_STATNAME: counters.available, EWT_STATNAME: counters.EWT, TALKINGAGENT_STATNAME: counters.Talking}}
        self.notifier.on_stat_changed(message)

    def _compute_nb_of_logged_agents(self, queueid):
        nb_of_agent_logged = 0
        for agentid in self.logged_agents:
            if queueid in self.queues_of_agent[agentid]:
                nb_of_agent_logged += 1
        return nb_of_agent_logged

    def _notify_change(self, queueid):
        self.notifier.on_stat_changed(
            {
                queueid: {
                    LOGGEDAGENT_STATNAME: self._compute_nb_of_logged_agents(queueid)
                }
            }
        )

    def send_all_stats(self, connection_cti):
        logger.info('collect statistics')
        for queueid in self.queues:
            self.notifier.send_statistic(
                {
                    queueid: {
                        LOGGEDAGENT_STATNAME: self._compute_nb_of_logged_agents(queueid)
                    }
                }, connection_cti)

    def subscribe_to_queue_member(self, queue_member_notifier):
        queue_member_notifier.subscribe_to_queue_member_add(self.on_queue_member_added)
        queue_member_notifier.subscribe_to_queue_member_remove(self.on_queue_member_removed)
