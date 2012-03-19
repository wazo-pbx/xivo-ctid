#!/usr/bin/python
# vim: set fileencoding=utf-8 :

# Copyright (C) 2007-2012  Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Pro-formatique SARL. See the LICENSE file at top of the
# source tree or delivered in the installable package in which XiVO CTI Server
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

from tests.mock import Mock, call, ANY
from xivo_cti.services.queuemember_service_manager import QueueMemberServiceManager


class TestQueueMemberServiceManager(unittest.TestCase):

    def setUp(self):
        self.queuemember_service_manager = QueueMemberServiceManager()

    def test_update_config(self):
        self.queuemember_service_manager.queuemember_dao = Mock()
        self.queuemember_service_manager.innerdata_dao = Mock()
        self.queuemember_service_manager.delta_computer = Mock()
        self.queuemember_service_manager.queuemember_notifier = Mock()

        self.queuemember_service_manager.update_config()

        dao_method_calls = self.queuemember_service_manager.queuemember_dao.method_calls
        innerdata_dao_method_calls = self.queuemember_service_manager.innerdata_dao.method_calls
        delta_computer_method_calls = self.queuemember_service_manager.delta_computer.method_calls
        notifier_method_calls = self.queuemember_service_manager.queuemember_notifier.method_calls
        self.assertTrue(dao_method_calls == [call.get_queuemembers()])
        self.assertTrue(innerdata_dao_method_calls == [call.get_queuemembers_config()])
        self.assertTrue(delta_computer_method_calls == [call.compute_delta(ANY,ANY)])
        self.assertTrue(notifier_method_calls == [call.queuemember_config_updated(ANY)])
