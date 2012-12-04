# -*- coding: utf-8 -*-

# XiVO CTI Server

# Copyright (C) 2007-2012  Avencall'
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

import unittest
from xivo_cti.cti_daolist import DaoList, UnknownListName
from tests.mock import Mock


class TestDaoList(unittest.TestCase):

    def setUp(self):
        self.daolist = DaoList('')

    def test_get_with_user(self):
        user_id = 1
        expected_result = {
            1: {
                'firtname': 'henri',
                'lstname': 'bob'
            }
        }
        self.daolist.listname = 'users'
        self.daolist._get_user = Mock()
        self.daolist._get_user.return_value = expected_result

        result = self.daolist.get(user_id)

        self.daolist._get_user.assert_called_once_with(user_id)
        self.assertEquals(result, expected_result)

    def test_get_with_agents(self):
        agent_id = 1
        expected_result = {
            1: {
                'firtname': 'henri',
                'lstname': 'bob'
            }
        }
        self.daolist.listname = 'agents'
        self.daolist._get_agent = Mock()
        self.daolist._get_agent.return_value = expected_result

        result = self.daolist.get(agent_id)

        self.daolist._get_agent.assert_called_once_with(agent_id)
        self.assertEquals(result, expected_result)

    def test_get_with_unknown_listname(self):
        self.daolist.listname = 'unknown'

        self.assertRaises(UnknownListName, self.daolist.get, 1)

    def test_get_with_no_result(self):
        user_id = 1
        self.daolist.listname = 'users'
        self.daolist._get_user = Mock()
        self.daolist._get_user.side_effect = LookupError

        result = self.daolist.get(user_id)

        self.assertEquals(result, {})
