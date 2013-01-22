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

from xivo_cti.cti.commands.getlist import GetList
from xivo_cti.cti.cti_command import CTICommand
from xivo_cti.cti.cti_command_factory import CTICommandFactory


class ListID(GetList):

    COMMAND_CLASS = 'getlist'
    FUNCTION_NAME = 'listid'

    required_fields = [CTICommand.CLASS, GetList.FUNCTION, GetList.LIST_NAME, GetList.IPBX_ID]
    conditions = [(CTICommand.CLASS, COMMAND_CLASS),
                  (GetList.FUNCTION, FUNCTION_NAME)]
    _callbacks = []
    _callbacks_with_params = []

    def __init__(self):
        super(ListID, self).__init__()
        self.function = self.FUNCTION_NAME

    def get_reply_list(self, item_list):
        return {CTICommand.CLASS: GetList.COMMAND_CLASS,
                GetList.FUNCTION: ListID.FUNCTION_NAME,
                'list': item_list,
                GetList.LIST_NAME: self.list_name,
                'replyid': self.commandid,
                GetList.IPBX_ID: self.ipbx_id}

CTICommandFactory.register_class(ListID)
