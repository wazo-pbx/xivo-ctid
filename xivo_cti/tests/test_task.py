# -*- coding: utf-8 -*-
# Copyright (C) 2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

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
