# -*- coding: utf-8 -*-
# Copyright (C) 2007-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

import unittest

from xivo_cti.cti.commands.switchboard_directory_search import SwitchboardDirectorySearch


class TestSwitchboardDirectorySearch(unittest.TestCase):

    _command_id = 1171069123
    _pattern = 'dkfj'
    _msg_dict = {'class': SwitchboardDirectorySearch.class_name,
                 'pattern': _pattern}

    def test_from_dict(self):
        switchboard_directory_search = SwitchboardDirectorySearch.from_dict(self._msg_dict)

        self.assertEqual(switchboard_directory_search.pattern, self._pattern)
