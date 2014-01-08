# -*- coding: utf-8 -*-

# Copyright (C) 2013-2014 Avencall
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
from hamcrest import assert_that
from hamcrest import equal_to

from xivo_cti.model.voicemail_destination import VoicemailDestination
from xivo_dao import extensions_dao
from xivo_cti import dao


class TestVoicemailDestination(unittest.TestCase):

    def test_to_exten(self):
        vm_id = 2
        vm_number = '4444'
        call_vm_exten = '*97.'
        expected = '*974444'
        extensions_dao.exten_by_name = Mock(return_value=call_vm_exten)
        dao.voicemail = Mock(dao.voicemail_dao.VoicemailDAO)
        dao.voicemail.get_number.return_value = vm_number
        d = VoicemailDestination('voicemail', None, vm_id)

        assert_that(d.to_exten(), equal_to(expected), 'Call voicemail extension')

        extensions_dao.exten_by_name.assert_called_once_with('vmboxslt')
