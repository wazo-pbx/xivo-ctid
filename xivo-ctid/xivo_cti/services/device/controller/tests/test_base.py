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

from hamcrest import assert_that
from hamcrest import equal_to
from mock import Mock
from unittest import TestCase
from xivo_cti.xivo_ami import AMIClass
from xivo_cti.services.device.controller import base
from xivo_dao.data_handler.device.model import Device


class TestBaseController(TestCase):

    def setUp(self):
        self._ami = Mock(AMIClass)

    def test_base_controller_ami_field(self):
        c = base.BaseController(self._ami)

        assert_that(c._ami, equal_to(self._ami))

    def test_answer_function_with_device_exists(self):
        c = base.BaseController(self._ami)

        c.answer(Device())
