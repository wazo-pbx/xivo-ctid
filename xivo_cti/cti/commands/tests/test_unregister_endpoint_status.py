# -*- coding: utf-8 -*-
# Copyright (C) 2015 Avencall
# SPDX-License-Identifier: GPL-3.0+

import unittest

from ..unregister_endpoint_status import UnregisterEndpointStatus
from hamcrest import assert_that
from hamcrest import contains
from hamcrest import equal_to


class TestUnregisterEndpointStatus(unittest.TestCase):

    def setUp(self):
        self.commandid = 2135344535
        self.msg = {
            'class': 'unregister_endpoint_status',
            'endpoint_ids': [
                ['xivo_uuid', 42],
                ['other_uuid', 12],
            ],
            'commandid': self.commandid,
        }

    def test_from_dict(self):
        cmd = UnregisterEndpointStatus.from_dict(self.msg)

        assert_that(cmd.endpoint_ids, contains(('xivo_uuid', 42), ('other_uuid', 12)))
        assert_that(cmd.commandid, equal_to(self.commandid))
