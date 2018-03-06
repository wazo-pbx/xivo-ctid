# -*- coding: utf-8 -*-
# Copyright (C) 2013-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

import unittest

from xivo_cti.model.destination_factory import DestinationFactory, UnimplementedDestinationException
from xivo_cti.model.consult_voicemail_destination import ConsultVoicemailDestination
from xivo_cti.model.extension_destination import ExtensionDestination
from xivo_cti.model.voicemail_destination import VoicemailDestination

from hamcrest import assert_that
from hamcrest import equal_to


class TestDestinationFactory(unittest.TestCase):

    def test_make_exten(self):
        url = 'exten:xivo/1234'
        d = DestinationFactory.make_from(url)

        assert_that(isinstance(d, ExtensionDestination), 'Instance type is ExtensionDestination')

    def test_make_voicemail(self):
        url = 'voicemail:xivo/12'
        d = DestinationFactory.make_from(url)

        assert_that(isinstance(d, VoicemailDestination), 'Instance type is VoicemailDestination')

    def test_make_consult_voicemail(self):
        url = 'vm_consult:xivo/666'
        d = DestinationFactory.make_from(url)

        assert_that(isinstance(d, ConsultVoicemailDestination), 'Instance type is ConsultVoicemailDestination')

    def test_make_unknown(self):
        url = 'invalid_destination_url:xivo/132'

        self.assertRaises(UnimplementedDestinationException, DestinationFactory.make_from, url)

    def test_parse_url_exten(self):
        exten = '+12 34'
        ipbxid = 'xivo'
        exten_url = 'exten:{0}/{1}'.format(ipbxid, exten)

        expected = ('exten', ipbxid, exten)

        assert_that(DestinationFactory._parse(exten_url), equal_to(expected), 'Parsed exten URL')

    def test_parse_url_invalid(self):
        self.assertRaises(ValueError, DestinationFactory._parse, '1234')

    def test_is_destination_url(self):
        url = 'voicemail:xivo/1234'

        assert_that(DestinationFactory.is_destination_url(url), equal_to(True), 'Is a valid URL')
