# -*- coding: utf-8 -*-
# Copyright (C) 2007-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

import unittest

from hamcrest import assert_that
from hamcrest import equal_to
from xivo_cti.cti.commands.call_form_result import CallFormResult


class TestCallFormResult(unittest.TestCase):

    def setUp(self):
        self._commandid = 1234556678
        self._variables = {
            'XIVOFORM_lastname': 'Manning',
            'XIVOFORM_firstname': 'Preston',
        }
        self._message = {
            'class': 'call_form_result',
            'commandid': self._commandid,
            'infos': {
                'buttonname': 'saveandclose',
                'variables': self._variables,
            },
        }

    def test_from_dict(self):
        call_form_result = CallFormResult.from_dict(self._message)

        assert_that(call_form_result.variables, equal_to(self._variables))
