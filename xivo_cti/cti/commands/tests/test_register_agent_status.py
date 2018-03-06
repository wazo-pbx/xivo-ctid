# -*- coding: utf-8 -*-
# Copyright 2015-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import unittest

from hamcrest import assert_that
from hamcrest import contains
from hamcrest import equal_to

from ..register_agent_status import RegisterAgentStatus


class TestRegisterAgentStatus(unittest.TestCase):

    def setUp(self):
        self.commandid = 2135344535
        self.msg = {
            'class': 'register_agent_status',
            'agent_ids': [
                ['xivo_uuid', 42],
                ['other_uuid', 12],
            ],
            'commandid': self.commandid,
        }

    def test_from_dict(self):
        cmd = RegisterAgentStatus.from_dict(self.msg)

        assert_that(cmd.agent_ids, contains(('xivo_uuid', 42), ('other_uuid', 12)))
        assert_that(cmd.commandid, equal_to(self.commandid))
