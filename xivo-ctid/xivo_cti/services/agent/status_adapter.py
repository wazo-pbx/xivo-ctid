# -*- coding: utf-8 -*-

# Copyright (C) 2007-2014 Avencall
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
from xivo.asterisk.extension import Extension
from xivo_cti.model.endpoint_event import EndpointEvent


logger = logging.getLogger(__name__)


class AgentStatusAdapter(object):

    def __init__(self, agent_status_router, endpoint_notifier, call_storage):
        self._status_router = agent_status_router
        self._endpoint_notifier = endpoint_notifier
        self._call_storage = call_storage
        self._agent_extensions = {}

    def handle_endpoint_event(self, endpoint_event):
        extension = endpoint_event.extension
        try:
            agent_id = agent_status_dao.get_agent_id_from_extension(extension.number, extension.context)
        except LookupError:
            logger.debug('endpoint %s has no agent', endpoint_event.extension)
            self._endpoint_notifier.unsubscribe_from_status_changes(extension, self.handle_endpoint_event)
        else:
            self._status_router.route(agent_id, endpoint_event)

    def subscribe_to_agent_events(self, agent_id):
        try:
            number, context = agent_status_dao.get_extension_from_agent_id(agent_id)
        except LookupError:
            logger.debug('agent with id %s is not logged', agent_id)
        else:
            extension = Extension(number, context, is_internal=True)
            self._new_subscription(extension, agent_id)

    def unsubscribe_from_agent_events(self, agent_id):
        extension = self._agent_extensions.pop(agent_id, None)
        if extension:
            self._endpoint_notifier.unsubscribe_from_status_changes(extension, self.handle_endpoint_event)

    def subscribe_all_logged_agents(self):
        for agent_id in agent_status_dao.get_logged_agent_ids():
            self.subscribe_to_agent_events(agent_id)

    def _new_subscription(self, extension, agent_id):
        self._agent_extensions[agent_id] = extension
        self._endpoint_notifier.subscribe_to_status_changes(extension, self.handle_endpoint_event)
        endpoint_status = self._call_storage.get_status_for_extension(extension)
        calls = self._call_storage.find_all_calls_for_extension(extension)
        event = EndpointEvent(extension, endpoint_status, calls)
        self._status_router.route(agent_id, event)
