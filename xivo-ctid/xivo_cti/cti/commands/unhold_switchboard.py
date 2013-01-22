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


class UnholdSwitchboard(CTICommand):

    COMMAND_CLASS = 'unhold_switchboard'
    UNIQUE_ID = 'unique_id'

    required_fields = [CTICommand.CLASS, UNIQUE_ID]
    conditions = [(CTICommand.CLASS, COMMAND_CLASS)]
    _callbacks = []
    _callbacks_with_params = []

    def _init_from_dict(self, msg):
        super(UnholdSwitchboard, self)._init_from_dict(msg)
        self.unique_id = msg.get(self.UNIQUE_ID)


CTICommandFactory.register_class(UnholdSwitchboard)
