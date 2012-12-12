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

from xivo_cti.dao.agent_dao import AgentDAO
from xivo_cti.dao.channel_dao import ChannelDAO
from xivo_cti.dao.queue_dao import QueueDAO
from xivo_cti.dao.user_dao import UserDAO
from xivo_cti.dao.innerdata_dao import InnerdataDAO

agent = None
channel = None
queue = None
user = None
innerdata = None


def instanciate_dao(innerdata_obj, queue_member_manager):
    global agent
    agent = AgentDAO(innerdata_obj, queue_member_manager)
    global channel
    channel = ChannelDAO(innerdata_obj)
    global queue
    queue = QueueDAO(innerdata_obj)
    global user
    user = UserDAO(innerdata_obj)
    global innerdata
    innerdata = InnerdataDAO(innerdata_obj)
