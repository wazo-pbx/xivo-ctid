# -*- coding: utf-8 -*-
# Copyright (C) 2007-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

import unittest

from xivo_cti.cti.commands.resume_switchboard import ResumeSwitchboard


class TestResumeSwitchboard(unittest.TestCase):

    def setUp(self):
        self.commandid = 125731893
        self.resume_switchboard_message = {
            'class': 'resume_switchboard',
            'unique_id': '123456.66',
            'commandid': self.commandid,
        }

    def test_from_dict(self):
        resume_switchboard = ResumeSwitchboard.from_dict(self.resume_switchboard_message)

        self.assertEqual(resume_switchboard.commandid, self.commandid)
        self.assertEqual(resume_switchboard.unique_id, self.resume_switchboard_message['unique_id'])
