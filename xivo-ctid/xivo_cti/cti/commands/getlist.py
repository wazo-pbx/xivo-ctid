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
# contracted with Avencall. See the LICENSE file at top of the souce tree
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

from xivo_cti.cti.cti_command import CTICommand
from xivo_cti.cti.cti_command_factory import CTICommandFactory


class GetList(CTICommand):

    COMMAND_CLASS = 'getlist'

    FUNCTION = 'function'
    LIST_NAME = 'listname'
    ITEM_ID = 'tid'
    IPBX_ID = 'tipbxid'

    required_fields = [CTICommand.CLASS, FUNCTION, LIST_NAME, IPBX_ID]
    conditions = [(CTICommand.CLASS, COMMAND_CLASS)]
    _callbacks = []
    _callbacks_with_params = []

    def __init__(self):
        super(GetList, self).__init__()
        self.command_class = self.COMMAND_CLASS
        self.function = None
        self.list_name = None
        self.item_id = None
        self.ipbx_id = None

    def _init_from_dict(self, msg):
        super(GetList, self)._init_from_dict(msg)
        self.function = msg[self.FUNCTION]
        self.list_name = msg[self.LIST_NAME]
        self.item_id = msg.get(self.ITEM_ID)
        self.ipbx_id = msg[self.IPBX_ID]

CTICommandFactory.register_class(GetList)
