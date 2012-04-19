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
from xivo_cti.dao.alchemy import dbconnection
from xivo_cti.dao.alchemy.queuemember import QueueMember
from xivo_cti.dao.alchemy.base import Base
from xivo_cti.dao.queuememberdao import QueueMemberDAO
from xivo_cti.dao.helpers.queuemember_formatter import QueueMemberFormatter

class TestQueueMemberDAO(unittest.TestCase):

    def test_get_queuemembers(self):
        session = Mock()
        queuemember_dao = QueueMemberDAO(session)
        old_queuemember_formatter = QueueMemberFormatter.format_queuemembers
        QueueMemberFormatter.format_queuemembers = Mock()
        expected_session_calls = [call.query(ANY)]
        expected_formatter_calls = [call.QueueMemberFormatter.format_queuemember]

        result = queuemember_dao.get_queuemembers()

        try:
            self.assertEqual(session.method_calls, expected_session_calls)
            self.assertTrue(QueueMemberFormatter.format_queuemembers.called)
        finally:
            QueueMemberFormatter.format_queuemembers = old_queuemember_formatter
