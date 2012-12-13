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
# contracted with Avencall. See the LICENSE file at top of the source tree
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


class Directory(CTICommand):

    COMMAND_CLASS = 'directory'

    PATTERN = 'pattern'
    HEADERS = 'headers'
    RESULT_LIST = 'resultlist'
    STATUS = 'status'

    STATUS_OK = 'ok'

    required_fields = [CTICommand.CLASS]
    conditions = [(CTICommand.CLASS, COMMAND_CLASS)]
    _callbacks = []
    _callbacks_with_params = []

    def __init__(self):
        super(Directory, self).__init__()
        self.command_class = self.COMMAND_CLASS
        self.pattern = None

    def _init_from_dict(self, msg):
        super(Directory, self)._init_from_dict(msg)
        self.pattern = msg.get(self.PATTERN)

    def get_reply_list(self, headers, results):
        return {self.CLASS: self.COMMAND_CLASS,
                self.HEADERS: headers,
                self.REPLYID: self.commandid,
                self.RESULT_LIST: results,
                self.STATUS: self.STATUS_OK}

CTICommandFactory.register_class(Directory)
