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

from mock import Mock
from hamcrest import *

from xivo_cti.model.consult_voicemail_destination import ConsultVoicemailDestination
from xivo_dao import extensions_dao

class TestConsultVoicemail(unittest.TestCase):

    def test_to_exten(self):
        consult_vm_exten = '*98'
        extensions_dao.exten_by_name = Mock(return_value=consult_vm_exten)
        d = ConsultVoicemailDestination('vm_consult', None, None)

        assert_that(d.to_exten(), equal_to(consult_vm_exten), 'Call voicemail extension')

        extensions_dao.exten_by_name.assert_called_once_with('vmusermsg')
