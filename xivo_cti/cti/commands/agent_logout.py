# -*- coding: utf-8 -*-
# Copyright (C) 2007-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_cti.cti.cti_command import CTICommandClass


def _match(msg):
    return msg['command'] == 'agentlogout'


def _parse(msg, command):
    command.agent_id = msg.get('agentids')


AgentLogout = CTICommandClass('ipbxcommand', _match, _parse)
AgentLogout.add_to_registry()
