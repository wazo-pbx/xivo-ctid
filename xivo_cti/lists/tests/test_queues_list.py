# -*- coding: utf-8 -*-

# Copyright (C) 2014 Avencall
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

import unittest
from mock import Mock
from xivo_cti.lists.queues_list import QueuesList


class TestQueuesList(unittest.TestCase):

    def setUp(self):
        innerdata = Mock()
        self.queues_list = QueuesList(innerdata)

    def _set_keeplist(self, keeplist):
        self.queues_list.keeplist = keeplist
        self.queues_list._init_reverse_dictionary()
