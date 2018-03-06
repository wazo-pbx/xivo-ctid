# -*- coding: utf-8 -*-
# Copyright (C) 2013-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

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
