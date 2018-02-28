# -*- coding: utf-8 -*-
# Copyright (C) 2013-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

import unittest

from mock import Mock
from hamcrest import assert_that
from hamcrest import equal_to

from xivo_cti.model.consult_voicemail_destination import ConsultVoicemailDestination
from xivo_dao import extensions_dao


class TestConsultVoicemail(unittest.TestCase):

    def test_to_exten(self):
        consult_vm_exten = '*98'
        extensions_dao.exten_by_name = Mock(return_value=consult_vm_exten)
        d = ConsultVoicemailDestination('vm_consult', None, None)

        assert_that(d.to_exten(), equal_to(consult_vm_exten), 'Call voicemail extension')

        extensions_dao.exten_by_name.assert_called_once_with('vmusermsg')
