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
from mock import Mock, call
from xivo_cti.dao.innerdatadao import InnerdataDAO
from xivo_cti.tools.delta_computer import DictDelta


class TestInnerdataDAO(unittest.TestCase):

    def setUp(self):
        self.innerdata_dao = InnerdataDAO()
        self.innerdata_dao.innerdata = Mock()
        self.queuemember1 = {'queuemember1_id': {'queue_name': 'queue1',
                                                 'interface': 'agent1',
                                                 'membership': 'static'}}
        self.queuemember2 = {'queuemember2_id': {'queue_name': 'queue2',
                                                 'interface': 'agent2',
                                                 'membership': 'dynamic'}}
        self.queuemember3 = {'queuemember3_id': {'queue_name': 'queue3',
                                                 'interface': 'agent3',
                                                 'membership': 'static'}}
        self.allqueuemembers = {}
        self.allqueuemembers.update(self.queuemember1)
        self.allqueuemembers.update(self.queuemember2)
        self.allqueuemembers.update(self.queuemember3)

    def test_get_queuemembers_config(self):
        expected_result = self.allqueuemembers
        self.innerdata_dao.innerdata.queuemembers_config = self.allqueuemembers

        result = self.innerdata_dao.get_queuemembers_config()

        self.assertEqual(result, expected_result)

    def test_get_queuemembers_static(self):
        self.innerdata_dao.innerdata.queuemembers_config = self.allqueuemembers
        expected_result = {}
        expected_result.update(self.queuemember1)
        expected_result.update(self.queuemember3)

        result = self.innerdata_dao.get_queuemembers_static()

        self.assertEqual(result, expected_result)

    def test_apply_queuemember_delta_add(self):
        new_queuemembers = {}
        new_queuemembers.update(self.queuemember2)
        new_queuemembers.update(self.queuemember3)
        input_delta = DictDelta(new_queuemembers, {}, [])
        expected_result = self.allqueuemembers
        self.innerdata_dao.innerdata.queuemembers_config = {}
        self.innerdata_dao.innerdata.queuemembers_config.update(self.queuemember1)

        self.innerdata_dao.apply_queuemember_delta(input_delta)

        self.assertEqual(self.innerdata_dao.innerdata.queuemembers_config, expected_result)

    def test_apply_queuemember_delta_delete(self):
        removed_queuemembers = ['queuemember1_id', 'queuemember2_id']
        input_delta = DictDelta({}, {}, removed_queuemembers)
        expected_result = self.queuemember3
        self.innerdata_dao.innerdata.queuemembers_config = {}
        self.innerdata_dao.innerdata.queuemembers_config.update(self.allqueuemembers)

        self.innerdata_dao.apply_queuemember_delta(input_delta)

        self.assertEqual(self.innerdata_dao.innerdata.queuemembers_config, expected_result)

    def test_apply_queuemember_delta_change(self):
        changed_queuemembers = self.queuemember2
        changed_queuemembers['queuemember2_id']['queue_name'] = 'queue2_changed'
        input_delta = DictDelta({}, changed_queuemembers, [])
        expected_result = self.allqueuemembers
        expected_result.update(changed_queuemembers)
        self.innerdata_dao.innerdata.queuemembers_config = self.allqueuemembers

        self.innerdata_dao.apply_queuemember_delta(input_delta)

        self.assertEqual(self.innerdata_dao.innerdata.queuemembers_config, expected_result)

    def test_apply_queuemember_delta_add_and_change(self):
        new_queuemembers = self.queuemember1
        changed_queuemembers = self.queuemember2
        changed_queuemembers['queuemember2_id']['queue_name'] = 'queue2_changed'
        input_delta = DictDelta(new_queuemembers, changed_queuemembers, [])
        expected_result = self.allqueuemembers
        expected_result.update(changed_queuemembers)
        self.innerdata_dao.innerdata.queuemembers_config = {}
        self.innerdata_dao.innerdata.queuemembers_config.update(self.queuemember2)
        self.innerdata_dao.innerdata.queuemembers_config.update(self.queuemember3)

        self.innerdata_dao.apply_queuemember_delta(input_delta)

        self.assertEqual(self.innerdata_dao.innerdata.queuemembers_config, expected_result)

    def test_apply_queuemember_delta_change_and_delete(self):
        removed_queuemembers = ['queuemember1_id']
        changed_queuemembers = self.queuemember2
        changed_queuemembers['queuemember2_id']['queue_name'] = 'queue2_changed'
        input_delta = DictDelta({}, changed_queuemembers, removed_queuemembers)
        expected_result = changed_queuemembers
        expected_result.update(self.queuemember3)
        self.innerdata_dao.innerdata.queuemembers_config = self.allqueuemembers

        self.innerdata_dao.apply_queuemember_delta(input_delta)

        self.assertEqual(self.innerdata_dao.innerdata.queuemembers_config, expected_result)

    def test_apply_queuemember_delta_add_change_and_delete(self):
        new_queuemembers = {'queuemember1_id': {'queue_name': 'queue1',
                                                'interface': 'agent1'}}
        changed_queuemembers = {'queuemember2_id': {'queue_name': 'queue2_changed',
                                                    'interface': 'agent2'}}
        removed_queuemembers = ['queuemember3_id']
        input_delta = DictDelta(new_queuemembers, changed_queuemembers, removed_queuemembers)
        expected_result = new_queuemembers
        expected_result.update(changed_queuemembers)
        self.innerdata_dao.innerdata.queuemembers_config = self.allqueuemembers

        self.innerdata_dao.apply_queuemember_delta(input_delta)

        self.assertEqual(self.innerdata_dao.innerdata.queuemembers_config, expected_result)

    def test_delete_other_queuemembers_inexistant(self):
        self.innerdata_dao.innerdata.queuemembers_config = self.allqueuemembers
        expected_method_calls = []

        self.innerdata_dao._delete_other_queuemembers('queuemember0_id')

        innerdata_method_calls = self.innerdata_dao.innerdata.method_calls
        self.assertEqual(innerdata_method_calls, expected_method_calls)

    def test_delete_other_queuemembers_existant(self):
        self.innerdata_dao.innerdata.queuemembers_config = self.allqueuemembers
        expected_method_calls = [call.queuememberupdate('queue1', 'agent1')]

        self.innerdata_dao._delete_other_queuemembers('queuemember1_id')

        innerdata_method_calls = self.innerdata_dao.innerdata.method_calls
        self.assertEqual(innerdata_method_calls, expected_method_calls)


    def test_get_queuemember_inexistant(self):
        self.innerdata_dao.innerdata.queuemembers_config = {}

        self.assertRaises(KeyError, self.innerdata_dao.get_queuemember, ('queuemember1'))

    def test_get_queuemember_existant(self):
        self.innerdata_dao.innerdata.queuemembers_config = self.allqueuemembers
        expected_result = self.queuemember1['queuemember1_id']

        result = self.innerdata_dao.get_queuemember('queuemember1_id')

        self.assertEqual(result, expected_result)
