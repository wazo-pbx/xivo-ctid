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

from xivo_dao import agent_status_dao
from xivo_cti.model.extension import Extension


logger = logging.getLogger(__name__)


class AgentStatusAdapter(object):

    def __init__(self, status_router, call_notifier):
        self._status_router = status_router
        self._call_notifier = call_notifier
        self._agent_extensions = {}

    def handle_call_event(self, call_event):
        extension = call_event.extension
        try:
            agent_id = agent_status_dao.get_agent_id_from_extension(extension.number, extension.context)
        except LookupError:
            logger.debug('endpoint %s has no agent', call_event.extension)
            self._call_notifier.unsubscribe_from_status_changes(extension, self.handle_call_event)
        else:
            self._status_router.route(agent_id, call_event.status)

    def subscribe_to_agent_events(self, agent_id):
        try:
            number, context = agent_status_dao.get_extension_from_agent_id(agent_id)
        except LookupError:
            logger.debug('agent with id %s is not logged', agent_id)
        else:
            extension = Extension(number, context)
            self._agent_extensions[agent_id] = extension
            self._call_notifier.subscribe_to_status_changes(extension, self.handle_call_event)

    def unsubscribe_from_agent_events(self, agent_id):
        extension = self._agent_extensions.pop(agent_id, None)
        if extension:
            self._call_notifier.unsubscribe_from_status_changes(extension, self.handle_call_event)

    def subscribe_all_logged_agents(self):
        for agent_id in agent_status_dao.get_logged_agent_ids():
            number, context = agent_status_dao.get_extension_from_agent_id(agent_id)
            extension = Extension(number, context)
            self._call_notifier.subscribe_to_status_changes(extension, self.handle_call_event)
