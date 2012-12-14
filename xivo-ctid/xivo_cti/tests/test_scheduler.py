# -*- coding: utf-8 -*-

# XiVO CTI Server
#
# Copyright (C) 2007-2012  Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Avencall. See the LICENSE file at top of the source tree
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
from mock import Mock, patch
from xivo_cti.scheduler import Scheduler


class TestScheduler(unittest.TestCase):

    def setUp(self):
        self.scheduler = Scheduler()
        self.mock_pipe = Mock()
        self.scheduler.setup(self.mock_pipe)

    @patch('threading.Timer')
    def test_schedule(self, mock_timer):
        mock_timer_instance = Mock()
        mock_timer.return_value = mock_timer_instance
        mock_callback = Mock()
        timeout = 5

        self.scheduler.schedule(timeout, mock_callback)

        mock_timer.assert_called_once_with(timeout,
                                           self.scheduler.execute_callback,
                                           [mock_callback])
        mock_timer_instance.start.assert_called_once_with()

    @patch('threading.Timer')
    def test_schedule_args(self, mock_timer):
        mock_timer_instance = Mock()
        mock_timer.return_value = mock_timer_instance
        mock_callback = Mock()
        timeout = 5
        arguments = (1, 2, 'three')
        expected_timer_arguments = [mock_callback]
        expected_timer_arguments.extend(arguments)

        self.scheduler.schedule(timeout, mock_callback, 1, 2, 'three')

        mock_timer.assert_called_once_with(timeout,
                                           self.scheduler.execute_callback,
                                           expected_timer_arguments)
        mock_timer_instance.start.assert_called_once_with()

    @patch('os.write')
    def test_execute_callback(self, mock_os_write):
        callback_function = Mock()
        callback_args = ('arg1', 'arg2')

        self.scheduler.execute_callback(callback_function, *callback_args)

        callback_function.assert_called_once_with(*callback_args)
        mock_os_write.assert_called_once_with(self.mock_pipe, 'scheduler:callback\n')
