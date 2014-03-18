# -*- coding: utf-8 -*-

# Copyright (C) 2012-2014 Avencall
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
from xivo_cti import message_hook


class TestMessageHook(unittest.TestCase):

    def test_add_hook(self):
        params = [('class', 'event'),
                  ('field', 'value')]

        def func1(event):
            pass

        message_hook.add_hook(params, func1)

        self.assertTrue((params, func1) in message_hook._hooks)

        def func2(event):
            pass

        message_hook.add_hook(params, func2)

        self.assertTrue((params, func2) in message_hook._hooks)

    def test_run_hooks(self):
        event = {'class': 'event',
                 'field': 'value',
                 'other': 'not checked'}
        params = [('class', 'event'),
                  ('field', 'value')]
        func_1 = Mock()
        func_2 = Mock()

        message_hook.add_hook(params, func_1)
        message_hook.add_hook(params, func_2)

        message_hook.run_hooks(event)

        func_1.assert_called_once_with(event)
        func_2.assert_called_once_with(event)

    def test_event_match_conditions(self):
        event = {'one': 1,
                 'two': 'deux',
                 'three': None}
        conditions = [('one', 1), ('two', 'deux')]

        result = message_hook._event_match_conditions(event, tuple(conditions))

        self.assertTrue(result)
