# -*- coding: utf-8 -*-

# Copyright (C) 2007-2013 Avencall
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

from mock import Mock
from hamcrest import *
from xivo_cti import innerdata
from xivo_cti import dao


class TestVoicemailDAO(unittest.TestCase):

    def setUp(self):
        self.innerdata = Mock(innerdata.Safe)

    def test_get_number(self):
        vm_id = '3'
        vm_number = '3456'

        vm_config = Mock()
        vm_config.keeplist = {vm_id: {'mailbox': vm_number}}
        self.innerdata.xod_config = {'voicemails': vm_config}
        dao.voicemail = dao.VoicemailDAO(self.innerdata)

        assert_that(dao.voicemail.get_number(vm_id), equal_to(vm_number), 'Voicemail number')
