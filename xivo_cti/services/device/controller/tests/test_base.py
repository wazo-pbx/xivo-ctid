# -*- coding: utf-8 -*-
# Copyright (C) 2007-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

from hamcrest import assert_that
from hamcrest import equal_to
from mock import Mock
from unittest import TestCase
from xivo_cti.xivo_ami import AMIClass
from xivo_cti.services.device.controller import base


class TestBaseController(TestCase):

    def setUp(self):
        self._ami = Mock(AMIClass)

    def test_base_controller_ami_field(self):
        c = base.BaseController(self._ami)

        assert_that(c._ami, equal_to(self._ami))

    def test_answer_function_with_device_exists(self):
        c = base.BaseController(self._ami)

        c.answer(None)
