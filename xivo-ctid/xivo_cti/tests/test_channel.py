# -*- coding: utf-8 -*-

# Copyright (C) 2007-2013 Avencall
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

from hamcrest import *
from xivo_cti.channel import Channel


class TestChannel(unittest.TestCase):

    def test_has_extra_data(self):
        channel = Channel('local/1002@statcenter', 'statcenter', '1234.12')

        result = channel.has_extra_data('xivo', 'calleridname')

        self.assertFalse(result)

        channel.set_extra_data('xivo', 'calleridname', 'test')

        result = channel.has_extra_data('xivo', 'calleridname')

        self.assertTrue(result)

    def test_update_state(self):
        state = 'Ringing'

        channel = Channel('1001@my-ctx-00000', 'my-ctx', '1234567.33')

        channel.update_state(5, state)

        self.assertEqual(channel.state, 5)
        self.assertEqual(channel.properties['state'], state)

    def test_inherit(self):
        channel = Channel('SIP/child_channel-0', 'default', '111111.11')
        channel.extra_data['xivo'] = {'calleridname': 'Child caller id',
                                      'calleridnum': '6248',
                                      'child-only-key': 'child-only-value'}
        parent_channel = Channel('SIP/parent_channel-0', 'default', '222222.22')
        parent_channel.extra_data['xivo'] = {'calleridname': 'Parent caller id',
                                             'calleridnum': '9634',
                                             'parent-only-key': 'parent-only-value'}

        channel.inherit(parent_channel)

        self._assert_2_level_dict_is_a_recursive_subset_of(parent_channel.extra_data, channel.extra_data)
        self._assert_2_level_dicts_share_no_dict_instance(channel.extra_data, parent_channel.extra_data)

    def _assert_2_level_dict_is_a_recursive_subset_of(self, dict_subset, dict_superset):
        assert_that(dict_subset, has_items(is_in(dict_superset)))
        for (key_subset, inner_subset) in dict_subset.iteritems():
            assert_that(inner_subset, has_items(is_in(dict_superset[key_subset])))
            assert_that(inner_subset.values(), has_items(is_in(dict_superset[key_subset].values())))

    def _assert_2_level_dicts_share_no_dict_instance(self, dict_left, dict_right):
        assert_that(dict_left, is_not(same_instance(dict_right)))
        for (key_left, value_left) in dict_left.iteritems():
            if key_left in dict_right:
                assert_that(value_left, is_not(same_instance(dict_right[key_left])))
