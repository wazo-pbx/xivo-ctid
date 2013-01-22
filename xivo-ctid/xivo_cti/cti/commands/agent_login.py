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

from xivo_cti.cti.cti_command import CTICommand
from xivo_cti.cti.cti_command_factory import CTICommandFactory


class AgentLogin(CTICommand):

    COMMAND_CLASS = 'ipbxcommand'

    AGENT_PHONE_NUMBER = 'agentphonenumber'
    AGENT_IDS = 'agentids'

    required_fields = [CTICommand.CLASS, 'command']
    conditions = [(CTICommand.CLASS, COMMAND_CLASS), ('command', 'agentlogin')]
    _callbacks = []
    _callbacks_with_params = []

    def _init_from_dict(self, msg):
        super(AgentLogin, self)._init_from_dict(msg)
        self.agent_phone_number = msg.get(self.AGENT_PHONE_NUMBER)
        self.agent_id = msg.get(self.AGENT_IDS)

CTICommandFactory.register_class(AgentLogin)
