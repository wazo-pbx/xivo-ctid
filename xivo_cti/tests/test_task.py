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
from mock import Mock, sentinel
from xivo_cti.task import Task


class TestTask(unittest.TestCase):

    def test_run(self):
        function = Mock()

        task = Task(function, (sentinel.args1, sentinel.args2))
        task.run()

        function.assert_called_once_with(sentinel.args1, sentinel.args2)

    def test_run_with_exception(self):
        function = Mock(side_effect=Exception('foobar'))

        task = Task(function, ())
        task.run()

        function.assert_called_once_with()
