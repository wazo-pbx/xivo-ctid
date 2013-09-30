# -*- coding: utf-8 -*-

# Copyright (C) 2007-2013 Avencall
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
from xivo_cti.services.queue_member.common import format_queue_member_id
from xivo_cti.services.queue_member.member import QueueMember, QueueMemberState
from xivo_dao import queue_member_dao

logger = logging.getLogger('QueueMemberUpdater')


class QueueMemberUpdater(object):

    def __init__(self, queue_member_manager, ami_class):
        self._queue_member_manager = queue_member_manager
        self._ami_class = ami_class

    def on_initialization(self):
        self._add_dao_queue_members_on_init()
        # we need to request QueueStatus of all asterisk queue members but this
        # is actually done in the AMIInitializer class

    def _add_dao_queue_members_on_init(self):
        for dao_queue_member in queue_member_dao.get_queue_members_for_queues():
            queue_member = QueueMember.from_dao_queue_member(dao_queue_member)
            self._queue_member_manager._add_queue_member(queue_member)

    def _add_dao_queue_members_on_update(self):
        old_queue_member_ids = set(self._queue_member_manager.get_queue_members_id())
        new_queue_member_ids = set()
        for dao_queue_member in queue_member_dao.get_queue_members_for_queues():
            queue_name = dao_queue_member.queue_name
            member_name = dao_queue_member.member_name
            queue_member_id = format_queue_member_id(queue_name, member_name)
            new_queue_member_ids.add(queue_member_id)
            if queue_member_id not in old_queue_member_ids:
                queue_member = QueueMember.from_dao_queue_member(dao_queue_member)
                self._queue_member_manager._add_queue_member(queue_member)
                self._ask_member_queue_status(queue_member)
        obsolete_queue_member_ids = old_queue_member_ids - new_queue_member_ids
        return obsolete_queue_member_ids

    def _ask_member_queue_status(self, queue_member):
        self._ami_class.queuestatus(queue_member.queue_name, queue_member.member_name)

    def on_ami_agent_logoff(self, ami_event):
        agent_number = ami_event['AgentNumber']
        self._update_agent_queue_members_as_unlogged(agent_number)

    def _update_agent_queue_members_as_unlogged(self, agent_number):
        for queue_member in self._queue_member_manager.get_queue_members_by_agent_number(agent_number):
            new_state = queue_member.state.copy()
            new_state.update_as_unlogged_agent()
            self._queue_member_manager._update_queue_member(queue_member, new_state)

    def on_ami_agent_added_to_queue(self, ami_event):
        queue_name = ami_event['QueueName']
        agent_number = ami_event['AgentNumber']
        queue_member = QueueMember.from_ami_agent_added_to_queue(queue_name, agent_number)
        self._queue_member_manager._add_queue_member(queue_member)

    def on_ami_agent_removed_from_queue(self, ami_event):
        queue_name = ami_event['QueueName']
        agent_number = ami_event['AgentNumber']
        self._queue_member_manager._remove_queue_member_by_agent_number(queue_name, agent_number)

    def on_ami_queue_member(self, ami_event):
        queue_name = ami_event['Queue']
        member_name = ami_event['Name']
        queue_member = self._queue_member_manager.get_queue_member_by_name(queue_name, member_name)
        if queue_member:
            new_state = QueueMemberState.from_ami_queue_member(ami_event)
            self._queue_member_manager._update_queue_member(queue_member, new_state)

    def on_ami_queue_member_status(self, ami_event):
        queue_name = ami_event['Queue']
        member_name = ami_event['MemberName']
        queue_member = self._queue_member_manager.get_queue_member_by_name(queue_name, member_name)
        if queue_member is None:
            self._log_unknown_queue_member('status', queue_name, member_name)
        else:
            new_state = QueueMemberState.from_ami_queue_member_status(ami_event)
            self._queue_member_manager._update_queue_member(queue_member, new_state)

    def on_ami_queue_member_added(self, ami_event):
        queue_name = ami_event['Queue']
        member_name = ami_event['MemberName']
        queue_member = self._queue_member_manager.get_queue_member_by_name(queue_name, member_name)
        if queue_member is None:
            self._log_unknown_queue_member('added', queue_name, member_name)
        else:
            if not queue_member.is_agent():
                logger.info('ignoring queue member added event for %r: not an agent', queue_member.id)
            else:
                new_state = QueueMemberState.from_ami_queue_member_added(ami_event)
                self._queue_member_manager._update_queue_member(queue_member, new_state)

    def on_ami_queue_member_paused(self, ami_event):
        queue_name = ami_event['Queue']
        member_name = ami_event['MemberName']
        queue_member = self._queue_member_manager.get_queue_member_by_name(queue_name, member_name)
        if queue_member is None:
            self._log_unknown_queue_member('paused', queue_name, member_name)
        else:
            paused = bool(int(ami_event['Paused']))
            new_state = queue_member.state.copy()
            new_state.paused = paused
            self._queue_member_manager._update_queue_member(queue_member, new_state)

    def on_webi_update(self):
        obsolete_queue_member_ids = self._add_dao_queue_members_on_update()
        for queue_member_id in obsolete_queue_member_ids:
            self._queue_member_manager._remove_queue_member_by_id(queue_member_id)

    def _log_unknown_queue_member(self, event_name, queue_name, member_name):
        queue_member_id = format_queue_member_id(queue_name, member_name)
        logger.info('ignoring queue member %s event for %r: unknown or group member',
                    event_name, queue_member_id)

    def register_ami_events(self, ami_handler):
        ami_handler.register_userevent_callback('AgentLogoff', self.on_ami_agent_logoff)
        ami_handler.register_userevent_callback('AgentAddedToQueue', self.on_ami_agent_added_to_queue)
        ami_handler.register_userevent_callback('AgentRemovedFromQueue', self.on_ami_agent_removed_from_queue)
        ami_handler.register_callback('QueueMember', self.on_ami_queue_member)
        ami_handler.register_callback('QueueMemberStatus', self.on_ami_queue_member_status)
        ami_handler.register_callback('QueueMemberAdded', self.on_ami_queue_member_added)
        ami_handler.register_callback('QueueMemberPaused', self.on_ami_queue_member_paused)
