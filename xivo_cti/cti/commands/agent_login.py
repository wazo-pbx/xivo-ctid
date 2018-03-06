# -*- coding: utf-8 -*-
# Copyright (C) 2007-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_cti.cti.cti_command import CTICommandClass


def _match(msg):
    return msg['command'] == 'agentlogin'


def _parse(msg, command):
    command.agent_phone_number = msg.get('agentphonenumber')
    command.agent_id = msg.get('agentids')


AgentLogin = CTICommandClass('ipbxcommand', _match, _parse)
AgentLogin.add_to_registry()
