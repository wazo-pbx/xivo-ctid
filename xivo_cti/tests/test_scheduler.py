# -*- coding: utf-8 -*-

# Copyright (C) 2007-2014 Avencall
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
from mock import Mock, patch
from xivo_cti.scheduler import Scheduler


class TestScheduler(unittest.TestCase):

    def setUp(self):
        self.task_queue = Mock()
        self.scheduler = Scheduler(self.task_queue)

    @patch('threading.Timer')
    def test_schedule(self, mock_timer):
        mock_timer_instance = Mock()
        mock_timer.return_value = mock_timer_instance
        mock_callback = Mock()
        timeout = 5

        self.scheduler.schedule(timeout, mock_callback)

        mock_timer.assert_called_once_with(timeout,
                                           self.task_queue.put,
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
                                           self.task_queue.put,
                                           expected_timer_arguments)
        mock_timer_instance.start.assert_called_once_with()
