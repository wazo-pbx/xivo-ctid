# -*- coding: utf-8 -*-

# XiVO CTI Server
# Copyright (C) 2009-2012  Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Avencall. See the LICENSE file at top of the source tree
# or delivered in the installable package in which XiVO CTI Server is
# distributed for more details.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from mock import patch, Mock
from xivo_cti.dao.user_dao import UserDAO, NoSuchUserException, \
    NoSuchLineException
from xivo_cti.innerdata import Safe
import time
import unittest
from xivo_cti.lists.users_list import UsersList
from xivo_cti.lists.phones_list import PhonesList


class TestUserDAO(unittest.TestCase):

    def setUp(self):
        self._innerdata = Mock(Safe)
        self._userlist = Mock(UsersList)
        self._userlist.keeplist = {}
        self._phonelist = Mock(PhonesList)
        self._phonelist.keeplist = {}
        self._innerdata.xod_config = {
            'users': self._userlist,
            'phones': self._phonelist
        }
        self.dao = UserDAO(self._innerdata)

    def test__phone(self):
        line_id = 206
        self._phonelist.keeplist[line_id] = {
            'context': 'default',
            'protocol': 'sip',
            'number': '1234',
            'iduserfeatures': 5,
        }

        result = self.dao._phone(line_id)

        self.assertTrue(result, self._phonelist.keeplist[line_id])

    def test__phone_no_line(self):
        self.assertRaises(NoSuchLineException, self.dao._phone, 206)

    def test__user(self):
        user_id = 206
        self._userlist.keeplist[user_id] = {
            'firstname': 'toto'
        }

        result = self.dao._user(user_id)

        self.assertTrue(result, self._userlist.keeplist[user_id])

    def test__user_no_user(self):
        self.assertRaises(NoSuchUserException, self.dao._user, 206)

    @patch('xivo_dao.user_dao.enable_dnd')
    def test_set_dnd(self, enable_dnd):
        user_id = 1
        self._userlist.keeplist[user_id] = {'enablednd': False}

        self.dao.enable_dnd(user_id)

        enable_dnd.assert_called_once_with(user_id)
        self.assertTrue(self._userlist.keeplist[user_id]['enablednd'])

    @patch('xivo_dao.user_dao.disable_dnd')
    def test_unset_dnd(self, disable_dnd):
        user_id = 1
        self._userlist.keeplist[user_id] = {'enablednd': True}

        self.dao.disable_dnd(user_id)

        disable_dnd.assert_called_once_with(user_id)
        self.assertFalse(self._userlist.keeplist[user_id]['enablednd'])

    @patch('xivo_dao.user_dao.enable_filter')
    def test_enable_filter(self, enable_filter):
        user_id = 1
        self._userlist.keeplist[user_id] = {'incallfilter': False}

        self.dao.enable_filter(user_id)

        enable_filter.assert_called_once_with(user_id)
        self.assertTrue(self._userlist.keeplist[user_id]['incallfilter'], 'inner data not updated for filter')

    @patch('xivo_dao.user_dao.disable_filter')
    def test_disable_filter(self, disable_filter):
        user_id = 1
        self._userlist.keeplist[user_id] = {'incallfilter': True}

        self.dao.disable_filter(user_id)

        disable_filter.assert_called_once_with(user_id)
        self.assertFalse(self._userlist.keeplist[user_id]['incallfilter'], 'inner data not updated for filter')

    @patch('xivo_dao.user_dao.enable_unconditional_fwd')
    def test_enable_unconditional_fwd(self, enable_unconditional_fwd):
        user_id = 1
        destination = '765'
        self._userlist.keeplist[user_id] = {'enableunc': False,
                                            'destunc': '964'}

        self.dao.enable_unconditional_fwd(user_id, destination)

        enable_unconditional_fwd.assert_called_once_with(user_id, destination)
        self.assertEqual(self._userlist.keeplist[user_id]['enableunc'], True)
        self.assertEqual(self._userlist.keeplist[user_id]['destunc'], destination, 'inner data not updated for unconditional destination')

    @patch('xivo_dao.user_dao.disable_unconditional_fwd')
    def test_unconditional_fwd_disabled(self, disable_unconditional_fwd):
        user_id = 1
        destination = '765'
        self._userlist.keeplist[user_id] = {'enableunc': True,
                                            'destunc': destination}

        self.dao.disable_unconditional_fwd(user_id, destination)

        disable_unconditional_fwd.assert_called_once_with(user_id, destination)
        self.assertEqual(self._userlist.keeplist[user_id]['enableunc'], False)
        self.assertEqual(self._userlist.keeplist[user_id]['destunc'], destination, 'inner data not updated for unconditional destination')

    @patch('xivo_dao.user_dao.enable_rna_fwd')
    def test_rna_fwd_enabled(self, enable_rna_fwd):
        user_id = 1
        destination = '4321'
        self._userlist.keeplist[user_id] = {'enablerna': False,
                                            'destrna': '656'}

        self.dao.enable_rna_fwd(user_id, destination)

        enable_rna_fwd.assert_called_once_with(user_id, destination)
        self.assertEqual(self._userlist.keeplist[user_id]['enablerna'], True)
        self.assertEqual(self._userlist.keeplist[user_id]['destrna'], destination, 'inner data not updated for rna destination')

    @patch('xivo_dao.user_dao.disable_rna_fwd')
    def test_rna_fwd_disabled(self, disable_rna_fwd):
        user_id = 1
        destination = '4321'
        self._userlist.keeplist[user_id] = {'enablerna': True,
                                            'destrna': destination}

        self.dao.disable_rna_fwd(user_id, destination)

        disable_rna_fwd.assert_called_once_with(user_id, destination)
        self.assertEqual(self._userlist.keeplist[user_id]['enablerna'], False)
        self.assertEqual(self._userlist.keeplist[user_id]['destrna'], destination, 'inner data not updated for rna destination')

    @patch('xivo_dao.user_dao.enable_busy_fwd')
    def test_busy_fwd_enabled(self, enable_busy_fwd):
        user_id = 1
        destination = '435'
        self._userlist.keeplist[user_id] = {'enablebusy': False,
                                            'destbusy': '876'}

        self.dao.enable_busy_fwd(user_id, destination)

        enable_busy_fwd.assert_called_once_with(user_id, destination)
        self.assertEqual(self._userlist.keeplist[user_id]['enablebusy'], True)
        self.assertEqual(self._userlist.keeplist[user_id]['destbusy'], destination, 'inner data not updated for busy destination')

    @patch('xivo_dao.user_dao.disable_rna_fwd')
    def test_busy_fwd_disabled(self, disable_rna_fwd):
        user_id = 1
        destination = '435'
        self._userlist.keeplist[user_id] = {'enablebusy': True,
                                            'destbusy': destination}

        self.dao.disable_rna_fwd(user_id, destination)

        disable_rna_fwd.assert_called_once_with(user_id, destination)
        self.assertEqual(self._userlist.keeplist[user_id]['enablebusy'], True)
        self.assertEqual(self._userlist.keeplist[user_id]['destbusy'], destination, 'inner data not updated for busy destination')

    def test_disconnect(self):
        self.dao._innerdata = self._innerdata
        user_id = 1
        self._userlist = {}
        self._userlist[user_id] = {'connection': True,
                                   'last-logouttimestamp': None}
        self.dao._innerdata.xod_status = {'users': self._userlist}
        expected_userdata = {'connection': None,
                             'last-logouttimestamp': time.time()}

        self.dao.disconnect(user_id)

        result = self.dao._innerdata.xod_status['users'][user_id]
        self.assertEqual(expected_userdata['connection'], result['connection'])
        self.assertTrue(expected_userdata['last-logouttimestamp'] > time.time() - 1)

    def test_set_presence(self):
        self.dao._innerdata = self._innerdata
        presence = 'disconnected'
        user_id = 1
        self._userlist = {}
        self._userlist[user_id] = {'availstate': 'available'}
        self.dao._innerdata.xod_status = {'users': self._userlist}
        expected_userdata = {'availstate': presence}

        self.dao.set_presence(user_id, presence)

        result = self.dao._innerdata.xod_status['users'][user_id]
        self.assertEqual(expected_userdata['availstate'], result['availstate'])

    def test_get_line_identity(self):
        user_id = 206
        line_id = 607
        self._phonelist.keeplist[line_id] = {
            'context': 'default',
            'protocol': 'sip',
            'number': '1234',
            'iduserfeatures': user_id,
            'rules_order': 0,
            'identity': 'sip/a1b2c3',
            'initialized': False,
            'allowtransfer': True
        }
        self._userlist.keeplist[user_id] = {'linelist': [line_id]}

        expected = 'sip/a1b2c3'

        result = self.dao.get_line_identity(user_id)

        self.assertEqual(result, expected)

    def test_get_context(self):
        context = 'default'
        user_id = 206
        line_id = 607
        self._phonelist.keeplist[line_id] = {
            'context': context,
            'protocol': 'sip',
            'number': '1234',
            'iduserfeatures': user_id,
            'rules_order': 0,
            'identity': 'sip/a1b2c3',
            'initialized': False,
            'allowtransfer': True
        }
        self._userlist.keeplist[user_id] = {
            'linelist': [line_id]
        }

        expected = context

        result = self.dao.get_context(user_id)

        self.assertEqual(result, expected)

    @patch('xivo_dao.user_dao.get_context')
    def test_get_context_no_line(self, mock_get_context):
        context = 'default'
        user_id = 206
        self._userlist.keeplist[user_id] = {
        }
        mock_get_context.return_value = context

        self.dao.get_line = Mock(side_effect=NoSuchLineException())

        result = self.dao.get_context(user_id)

        self.assertEqual(result, context)

    def test_get_line_no_linelist_field(self):
        # Happens when the CTI server is starting
        context = 'default'
        user_id = 206
        line_id = 607
        self._phonelist.keeplist[line_id] = {
            'context': context,
            'protocol': 'sip',
            'number': '1234',
            'iduserfeatures': user_id,
            'rules_order': 0,
            'identity': 'sip/a1b2c3',
            'initialized': False,
            'allowtransfer': True
        }
        self._userlist.keeplist[user_id] = {
        }

        self.assertRaises(NoSuchLineException, self.dao.get_line, user_id)

    def test_get_line_user_not_exist(self):
        user_id = 206
        line_id = 607
        self._phonelist.keeplist[line_id] = {
            'context': 'default',
            'protocol': 'sip',
            'number': '1234',
            'iduserfeatures': user_id,
            'rules_order': 0,
            'identity': 'sip/a1b2c3',
            'initialized': False,
            'allowtransfer': True
        }
        self._userlist.keeplist = {}

        self.assertRaises(NoSuchUserException, self.dao.get_line, user_id)

    def test_get_line_line_not_exist(self):
        user_id = 206
        line_id = 607
        self._phonelist.keeplist = {}
        self._userlist.keeplist[user_id] = {
            'linelist': [line_id]
        }

        self.assertRaises(NoSuchLineException, self.dao.get_line, user_id)

    def test_get_cti_profile_id(self):
        user_id = 206
        self._userlist.keeplist[user_id] = {
            'firstname': 'toto',
            'cti_profile_id': 4
        }

        result = self.dao.get_cti_profile_id(user_id)

        self.assertEqual(result, 4)
