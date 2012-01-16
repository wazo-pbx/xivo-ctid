from xivo_cti.cti.commands.login_id import LoginID

import unittest


class Test(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_login_id(self):
        login_id = LoginID()
        self.assertEqual(login_id.command_class, 'login_id')
        self.assertEqual(login_id.commandid, None)
        self.assertEqual(login_id.company, None)
        self.assertEqual(login_id.git_date, None)
        self.assertEqual(login_id.git_hash, None)
        self.assertEqual(login_id.ident, None)
        self.assertEqual(login_id.lastlogout_datetime, None)
        self.assertEqual(login_id.lastlogout_stopper, None)
        self.assertEqual(login_id.userlogin, None)
        self.assertEqual(login_id.version, None)
        self.assertEqual(login_id.xivo_version, None)

    def test_from_dict(self):
        commandid = 476707713
        company = 'default'
        git_date = '1326300351'
        git_hash = '17484c6'
        ident = 'X11-LE-25439'
        datetime = '2012-01-13T08:34:19'
        stopper = 'disconnect'
        userlogin = 'test_user'
        version = '9999'
        xivo_version = '1.2'
        login_id = LoginID.from_dict({'class': "login_id",
                                      'commandid': commandid,
                                      'company': company,
                                      'git_date': git_date,
                                      'git_hash': git_hash,
                                      'ident': ident,
                                      'lastlogout-datetime': datetime,
                                      'lastlogout-stopper': stopper,
                                      'userlogin': userlogin,
                                      'version': version,
                                      'xivoversion': xivo_version})
        self.assertEqual(login_id.commandid, commandid)
        self.assertEqual(login_id.company, company)
        self.assertEqual(login_id.git_date, git_date)
        self.assertEqual(login_id.git_hash, git_hash)
        self.assertEqual(login_id.ident, ident)
        self.assertEqual(login_id.lastlogout_datetime, datetime)
        self.assertEqual(login_id.lastlogout_stopper, stopper)
        self.assertEqual(login_id.userlogin, userlogin)
        self.assertEqual(login_id.version, version)
        self.assertEqual(login_id.xivo_version, xivo_version)
