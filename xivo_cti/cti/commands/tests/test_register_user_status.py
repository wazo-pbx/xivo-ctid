# -*- coding: utf-8 -*-
# Copyright (C) 2015 Avencall
# SPDX-License-Identifier: GPL-3.0+

import unittest

from ..register_user_status import RegisterUserStatus
from hamcrest import assert_that
from hamcrest import contains
from hamcrest import equal_to


class TestRegisterUserStatus(unittest.TestCase):

    def setUp(self):
        self.commandid = 2135344535
        self.msg = {
            'class': 'register_user_status',
            'user_ids': [
                ['xivo_uuid', 42],
                ['other_uuid', 12],
            ],
            'commandid': self.commandid,
        }

    def test_from_dict(self):
        cmd = RegisterUserStatus.from_dict(self.msg)

        assert_that(cmd.user_ids, contains(('xivo_uuid', 42), ('other_uuid', 12)))
        assert_that(cmd.commandid, equal_to(self.commandid))
