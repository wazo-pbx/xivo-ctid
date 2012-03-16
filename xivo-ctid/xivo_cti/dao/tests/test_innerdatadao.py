# -*- coding: utf-8 -*-

# XiVO CTI Server
# Copyright (C) 2009-2012  Avencall
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
from mock import Mock
from xivo_cti.dao.innerdatadao import InnerdataDAO


class TestInnerdataDAO(unittest.TestCase):

    def test_get_queuemembers_config(self):
        innerdata_dao = InnerdataDAO()
        expected_result = {}
        expected_result['queuemember1_id'] = {}
        expected_result['queuemember1_id']['queue_name'] = 'queue1'
        expected_result['queuemember1_id']['interface'] = 'agent1'
        expected_result['queuemember1_id']['penalty'] = '0'
        expected_result['queuemember1_id']['call_limit'] = '0'
        expected_result['queuemember1_id']['paused'] = '0'
        expected_result['queuemember1_id']['commented'] = '0'
        expected_result['queuemember1_id']['usertype'] = 'agent'
        expected_result['queuemember1_id']['userid'] = '1'
        expected_result['queuemember1_id']['channel'] = 'chan1'
        expected_result['queuemember1_id']['category'] = 'queue'
        expected_result['queuemember1_id']['skills'] = ''
        expected_result['queuemember1_id']['state_interface'] = ''
        innerdata_dao.innerdata = Mock()
        innerdata_dao.innerdata.queuemembers_config = expected_result

        result = innerdata_dao.get_queuemembers_config()

        self.assertEqual(result, expected_result)
