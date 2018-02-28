# -*- coding: utf-8 -*-
# Copyright (C) 2015 Avencall
# SPDX-License-Identifier: GPL-3.0+

import logging

from xivo_cti.cti.cti_command import CTICommandClass

logger = logging.getLogger(__name__)


def _parse(msg, command):
    command.agent_ids = [(xivo_uuid, agent_id) for (xivo_uuid, agent_id) in msg['agent_ids']]


RegisterAgentStatus = CTICommandClass('register_agent_status_update', None, _parse)
RegisterAgentStatus.add_to_registry()
