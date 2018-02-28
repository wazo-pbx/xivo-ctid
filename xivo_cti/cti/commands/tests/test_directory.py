# -*- coding: utf-8 -*-
# Copyright (C) 2007-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

import unittest

from xivo_cti.cti.commands.directory import Directory


class TestDirectory(unittest.TestCase):

    _command_id = 1171069123
    _pattern = 'Test'
    _msg_dict = {'class': Directory.class_name, 'pattern': _pattern}

    def test_from_dict(self):
        directory = Directory.from_dict(self._msg_dict)

        self.assertEqual(directory.pattern, self._pattern)
