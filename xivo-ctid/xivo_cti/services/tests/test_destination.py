# -*- coding: utf-8 -*-

# Copyright (C) 2013 Avencall
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

from hamcrest import *
from mock import Mock

from xivo_cti.services.destination import Destination
from xivo_dao import extensions_dao
from xivo_cti import dao


class TestDestination(unittest.TestCase):

    def setUp(self):
        self.ipbxid = 'xivo'

    def test_to_exten_exten(self):
        number = '1234'
        exten_dest = Destination('exten', self.ipbxid, number)

        exten = exten_dest._to_exten_from_exten()

        assert_that(exten, equal_to(number), 'Called number')

    def test_to_exten_from_voicemail(self):
        vm_id = 2
        vm_number = '4444'
        call_vm_exten = '*97.'
        expected = '*974444'
        extensions_dao.exten_by_name = Mock(return_value=call_vm_exten)
        dao.voicemail = Mock(dao.voicemail_dao.VoicemailDAO)
        dao.voicemail.get_number.return_value = vm_number
        vm_dest = Destination('voicemail', self.ipbxid, vm_id)

        exten = vm_dest._to_exten_from_voicemail()

        assert_that(exten, equal_to(expected), 'Call voicemail extension')

        extensions_dao.exten_by_name.assert_called_once_with('vmboxslt')

    def test_to_exten_from_vm_consult(self):
        consult_vm_exten = '*98'
        extensions_dao.exten_by_name = Mock(return_value=consult_vm_exten)
        vm_dest = Destination('vm_consult', self.ipbxid, None)

        exten = vm_dest._to_exten_from_vm_consult()

        assert_that(exten, equal_to(consult_vm_exten), 'Call voicemail extension')

        extensions_dao.exten_by_name.assert_called_once_with('vmusermsg')

    def test_equality(self):
        d1 = Destination('one', 'two', 'three')
        self.assertTrue(d1 == Destination('one', 'two', 'three'))
        self.assertFalse(d1 == Destination('one', 'two', None))
        self.assertFalse(d1 == Destination('one', None, 'three'))
        self.assertFalse(d1 == Destination(None, 'two', 'three'))
