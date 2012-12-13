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
from xivo_cti.cti.commands.subscribe import Subscribe
from xivo_cti.cti.cti_command_factory import CTICommandFactory


class SubscribeQueueEntryUpdate(Subscribe):

    QUEUE_ID = 'queueid'
    MESSAGE_NAME = 'queueentryupdate'

    required_fields = [CTICommand.CLASS, Subscribe.MESSAGE, QUEUE_ID]
    conditions = [(CTICommand.CLASS, Subscribe.COMMAND_CLASS),
                  (Subscribe.MESSAGE, MESSAGE_NAME)]
    _callbacks, _callbacks_with_params = [], []

    def _init_from_dict(self, msg):
        super(SubscribeQueueEntryUpdate, self)._init_from_dict(msg)
        self.queue_id = int(msg[self.QUEUE_ID])

CTICommandFactory.register_class(SubscribeQueueEntryUpdate)
