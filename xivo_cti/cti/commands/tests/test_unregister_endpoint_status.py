# -*- coding: utf-8 -*-

# Copyright (C) 2015 Avencall
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
