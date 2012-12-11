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


class QueuePause(CTICommand):

    COMMAND_CLASS = 'ipbxcommand'

    COMMAND = 'queuepause'
    MEMBER = 'member'
    QUEUE = 'queue'

    required_fields = [CTICommand.CLASS, 'command']
    conditions = [(CTICommand.CLASS, COMMAND_CLASS), ('command', COMMAND)]
    _callbacks = []
    _callbacks_with_params = []

    def _init_from_dict(self, msg):
        super(QueuePause, self)._init_from_dict(msg)
        self.member = msg.get(self.MEMBER)
        self.queue = msg.get(self.QUEUE)

CTICommandFactory.register_class(QueuePause)
