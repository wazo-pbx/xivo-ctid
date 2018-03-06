# -*- coding: utf-8 -*-
# Copyright (C) 2007-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

import logging
from xivo_cti.model.endpoint_status import EndpointStatus
from xivo_cti.services.call.direction import CallDirection

logger = logging.getLogger(__name__)


class AgentStatusRouter(object):

    def __init__(self, agent_status_manager):
        self._status_manager = agent_status_manager

    def route(self, agent_id, event):
        if event.status == EndpointStatus.available:
            self._status_manager.device_not_in_use(agent_id)
        elif event.status == EndpointStatus.talking:
            if event.calls:
                direction = self._get_call_direction(event.extension, event.calls)
                is_internal = self._is_call_internal(event.calls)
                self._status_manager.device_in_use(agent_id, direction, is_internal)
            else:
                self._status_manager.device_in_use(agent_id, CallDirection.outgoing, True)

    def _get_call_direction(self, extension, calls):
        call = self._considered_call(calls)
        if extension == call.destination.extension:
            return CallDirection.incoming
        elif extension == call.source.extension:
            return CallDirection.outgoing

    def _is_call_internal(self, calls):
        call = self._considered_call(calls)
        return call.is_internal

    def _considered_call(self, calls):
        return calls[0]
