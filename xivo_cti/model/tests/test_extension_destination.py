# -*- coding: utf-8 -*-
# Copyright (C) 2013-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

import unittest

from hamcrest import assert_that
from hamcrest import equal_to

from xivo_cti.model.extension_destination import ExtensionDestination


class TestExtensionDestination(unittest.TestCase):

    def test_to_exten(self):
        number = '1234'
        d = ExtensionDestination('exten', None, number)

        assert_that(d.to_exten(), equal_to(number), 'Called number')
