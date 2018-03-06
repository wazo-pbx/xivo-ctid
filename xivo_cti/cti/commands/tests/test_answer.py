# -*- coding: utf-8 -*-
# Copyright (C) 2007-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

import unittest

from mock import sentinel
from xivo_cti.cti.commands.answer import Answer


class TestAnswer(unittest.TestCase):

    def setUp(self):
        self.answer_message = {
            'class': 'answer',
            'commandid': sentinel.commandid,
            'unique_id': sentinel.unique_id,
        }

    def test_from_dict(self):
        answer = Answer.from_dict(self.answer_message)

        self.assertEqual(answer.commandid, sentinel.commandid)
        self.assertEqual(answer.unique_id, sentinel.unique_id)
