# -*- coding: UTF-8 -*-

import unittest
from xivo_cti.cti_config import CTI_PROTOCOL_VERSION
from xivo_cti.cti.commands.login_id import LoginID


class Test(unittest.TestCase):

    def test_login_id(self):
        login_id = LoginID()
        self.assertEqual(login_id.command_class, 'login_id')
        self.assertEqual(login_id.commandid, None)
        self.assertEqual(login_id.company, None)
        self.assertEqual(login_id.ident, None)
        self.assertEqual(login_id.userlogin, None)
        self.assertEqual(login_id.xivo_version, None)

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
                                      'xivoversion': xivo_version})
        self.assertEqual(login_id.commandid, commandid)
        self.assertEqual(login_id.company, company)
        self.assertEqual(login_id.ident, ident)
        self.assertEqual(login_id.userlogin, userlogin)
        self.assertEqual(login_id.xivo_version, xivo_version)
