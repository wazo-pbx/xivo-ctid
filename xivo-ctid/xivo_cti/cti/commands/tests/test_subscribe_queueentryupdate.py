# vim: set fileencoding=utf-8 :
# XiVO CTI Server

# Copyright (C) 2007-2012  Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Pro-formatique SARL. See the LICENSE file at top of the
# source tree or deliverend in the installable package in which XiVO CTI Server
# is distributed for more details.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import unittest

from xivo_cti.cti.commands.subscribe_queue_entry_update import SubscribeQueueEntryUpdate


class TestSubscribeQueueEntryUpdate(unittest.TestCase):

    SUBSCRIBE_MSG = {'class': 'subscribe',
                     'message': 'queueentryupdate',
                     'queueid': '2'}

    def test_init_from_dict(self):
        sub_msg = SubscribeQueueEntryUpdate.from_dict(self.SUBSCRIBE_MSG)

        self.assertEquals(sub_msg.queue_id, 2)
