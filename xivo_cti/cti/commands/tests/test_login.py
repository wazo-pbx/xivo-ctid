# -*- coding: utf-8 -*-
# Copyright 2013-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import unittest

from xivo_cti import CTI_PROTOCOL_VERSION
from xivo_cti.cti.commands.login import LoginCapas, LoginID, LoginPass


class TestLoginId(unittest.TestCase):

    def test_from_dict(self):
        commandid = 476707713
        company = 'default'
        ident = 'X11-LE-25439'
        userlogin = 'test_user'
        xivo_version = CTI_PROTOCOL_VERSION
        login_id = LoginID.from_dict({'class': "login_id",
                                      'commandid': commandid,
                                      'company': company,
                                      'ident': ident,
                                      'userlogin': userlogin,
                                      'wazoversion': xivo_version})
        self.assertEqual(login_id.commandid, commandid)
        self.assertEqual(login_id.company, company)
        self.assertEqual(login_id.ident, ident)
        self.assertEqual(login_id.userlogin, userlogin)
        self.assertEqual(login_id.xivo_version, xivo_version)


class TestLoginPass(unittest.TestCase):

    def test_from_dict(self):
        password = '*&*foobar*&*'
        login_pass = LoginPass.from_dict({'class': 'login_pass',
                                          'password': password,
                                          'commandid': 'abc'})

        self.assertEqual(login_pass.password, password)


class TestLoginCapas(unittest.TestCase):

    def test_from_dict(self):
        state = 'away'
        profile_id = '42'

        login_capas = LoginCapas.from_dict({'class': 'login_capas',
                                            'state': state,
                                            'capaid': profile_id})

        self.assertEqual(login_capas.state, state)
        self.assertEqual(login_capas.capaid, 42)
