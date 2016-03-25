# -*- coding: utf-8 -*-

# Copyright (C) 2009-2016 Avencall
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

from mock import patch, Mock, sentinel
from xivo_cti.dao.user_dao import UserDAO, NoSuchUserException, \
    NoSuchLineException
from xivo_cti.innerdata import Safe
import time
import unittest
from hamcrest import assert_that
from hamcrest import equal_to
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
        line_id = '206'
        self._phonelist.keeplist[line_id] = {
            'context': 'default',
            'protocol': 'sip',
            'number': '1234',
        }

        result = self.dao._phone(line_id)

        self.assertTrue(result, self._phonelist.keeplist[line_id])

    def test__phone_no_line(self):
        self.assertRaises(NoSuchLineException, self.dao._phone, 206)

    def test__user(self):
        user_id = '206'
        self._userlist.keeplist[user_id] = {
            'firstname': 'toto'
        }

        result = self.dao._user(user_id)

        self.assertTrue(result, self._userlist.keeplist[user_id])

    def test__user_no_user(self):
        self.assertRaises(NoSuchUserException, self.dao._user, 206)

    def test_get_by_uuid(self):
        expected = self._userlist.keeplist['42'] = {'uuid': sentinel.uuid}

        result = self.dao.get_by_uuid(sentinel.uuid)

        assert_that(result, equal_to(expected))

    def test_get_by_uuid_not_found(self):
        self.assertRaises(NoSuchUserException, self.dao.get_by_uuid, sentinel.uuid)

    def test_fullname(self):
        user_id = '123'
        fullname = 'full'
        self._userlist.keeplist[user_id] = {'fullname': fullname}

        result = self.dao.get_fullname(user_id)

        assert_that(result, equal_to(fullname), 'User\'s fullname')

    def test_set_dnd(self):
        user_id = '1'
        self._userlist.keeplist[user_id] = {'enablednd': False}

        self.dao.set_dnd(user_id, True)

        self.assertTrue(self._userlist.keeplist[user_id]['enablednd'])

    def test_unset_dnd(self):
        user_id = '1'
        self._userlist.keeplist[user_id] = {'enablednd': True}

        self.dao.set_dnd(user_id, False)

        self.assertFalse(self._userlist.keeplist[user_id]['enablednd'])

    def test_set_incallfilter_enabled(self):
        user_id = '1'
        self._userlist.keeplist[user_id] = {'incallfilter': False}

        self.dao.incallfilter_enabled(user_id, True)

        self.assertTrue(self._userlist.keeplist[user_id]['incallfilter'], 'inner data not updated for filter')

    def test_unset_incallfilter_enabled(self):
        user_id = '1'
        self._userlist.keeplist[user_id] = {'incallfilter': True}

        self.dao.incallfilter_enabled(user_id, False)

        self.assertFalse(self._userlist.keeplist[user_id]['incallfilter'], 'inner data not updated for filter')

    @patch('xivo_cti.database.user_db.enable_service')
    def test_enable_unconditional_fwd(self, enable_service):
        user_id = '1'
        destination = '765'
        self._userlist.keeplist[user_id] = {'enableunc': False,
                                            'destunc': '964'}

        self.dao.enable_unconditional_fwd(user_id, destination)

        enable_service.assert_called_once_with(user_id, 'enableunc', 'destunc', destination)
        self.assertEqual(self._userlist.keeplist[user_id]['enableunc'], True)
        self.assertEqual(self._userlist.keeplist[user_id]['destunc'], destination, 'inner data not updated for unconditional destination')

    @patch('xivo_cti.database.user_db.disable_service')
    def test_unconditional_fwd_disabled(self, disable_service):
        user_id = '1'
        destination = '765'
        self._userlist.keeplist[user_id] = {'enableunc': True,
                                            'destunc': destination}

        self.dao.disable_unconditional_fwd(user_id, destination)

        disable_service.assert_called_once_with(user_id, 'enableunc', 'destunc', destination)
        self.assertEqual(self._userlist.keeplist[user_id]['enableunc'], False)
        self.assertEqual(self._userlist.keeplist[user_id]['destunc'], destination, 'inner data not updated for unconditional destination')

    @patch('xivo_cti.database.user_db.enable_service')
    def test_rna_fwd_enabled(self, enable_service):
        user_id = '1'
        destination = '4321'
        self._userlist.keeplist[user_id] = {'enablerna': False,
                                            'destrna': '656'}

        self.dao.enable_rna_fwd(user_id, destination)

        enable_service.assert_called_once_with(user_id, 'enablerna', 'destrna', destination)
        self.assertEqual(self._userlist.keeplist[user_id]['enablerna'], True)
        self.assertEqual(self._userlist.keeplist[user_id]['destrna'], destination, 'inner data not updated for rna destination')

    @patch('xivo_cti.database.user_db.disable_service')
    def test_rna_fwd_disabled(self, disable_service):
        user_id = '1'
        destination = '4321'
        self._userlist.keeplist[user_id] = {'enablerna': True,
                                            'destrna': destination}

        self.dao.disable_rna_fwd(user_id, destination)

        disable_service.assert_called_once_with(user_id, 'enablerna', 'destrna', destination)
        self.assertEqual(self._userlist.keeplist[user_id]['enablerna'], False)
        self.assertEqual(self._userlist.keeplist[user_id]['destrna'], destination, 'inner data not updated for rna destination')

    @patch('xivo_cti.database.user_db.enable_service')
    def test_busy_fwd_enabled(self, enable_service):
        user_id = '1'
        destination = '435'
        self._userlist.keeplist[user_id] = {'enablebusy': False,
                                            'destbusy': '876'}

        self.dao.enable_busy_fwd(user_id, destination)

        enable_service.assert_called_once_with(user_id, 'enablebusy', 'destbusy', destination)
        self.assertEqual(self._userlist.keeplist[user_id]['enablebusy'], True)
        self.assertEqual(self._userlist.keeplist[user_id]['destbusy'], destination, 'inner data not updated for busy destination')

    @patch('xivo_cti.database.user_db.disable_service')
    def test_busy_fwd_disabled(self, disable_service):
        user_id = '1'
        destination = '435'
        self._userlist.keeplist[user_id] = {'enablebusy': True,
                                            'destbusy': destination}

        self.dao.disable_busy_fwd(user_id, destination)

        disable_service.assert_called_once_with(user_id, 'enablebusy', 'destbusy', destination)
        self.assertEqual(self._userlist.keeplist[user_id]['enablebusy'], False)
        self.assertEqual(self._userlist.keeplist[user_id]['destbusy'], destination, 'inner data not updated for busy destination')

    def test_connect(self):
        self.dao._innerdata = self._innerdata
        user_id = '1'
        self._userlist = {}
        self._userlist[user_id] = {'connection': None}
        self.dao._innerdata.xod_status = {'users': self._userlist}

        self.dao.connect(user_id)

        result = self.dao._innerdata.xod_status['users'][user_id]

        expected_userdata = {'connection': 'yes'}
        self.assertEqual(expected_userdata['connection'], result['connection'])

    def test_disconnect(self):
        self.dao._innerdata = self._innerdata
        user_id = '1'
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

    def test_get_presence(self):
        self.dao._innerdata = self._innerdata
        self._userlist = {}
        user_id = '42'
        self._userlist[user_id] = {'availstate': sentinel.presence}
        self.dao._innerdata.xod_status = {'users': self._userlist}

        presence = self.dao.get_presence(user_id)

        assert_that(presence, equal_to(sentinel.presence))

    def test_set_presence(self):
        self.dao._innerdata = self._innerdata
        presence = 'disconnected'
        user_id = '1'
        self._userlist = {}
        self._userlist[user_id] = {'availstate': 'available'}
        self.dao._innerdata.xod_status = {'users': self._userlist}
        expected_userdata = {'availstate': presence}

        self.dao.set_presence(user_id, presence)

        result = self.dao._innerdata.xod_status['users'][user_id]
        self.assertEqual(expected_userdata['availstate'], result['availstate'])

    def test_get_line_identity(self):
        user_id = '206'
        line_id = '607'
        self._phonelist.keeplist[line_id] = {
            'context': 'default',
            'protocol': 'sip',
            'number': '1234',
            'identity': 'sip\/a1b2c3',
            'initialized': False,
            'allowtransfer': True
        }
        self._userlist.keeplist[user_id] = {'linelist': [line_id]}

        expected = 'sip/a1b2c3'

        result = self.dao.get_line_identity(user_id)

        self.assertEqual(result, expected)

    def test_get_context(self):
        context = 'default'
        user_id = '206'
        line_id = '607'
        self._phonelist.keeplist[line_id] = {
            'context': context,
            'protocol': 'sip',
            'number': '1234',
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

    @patch('xivo_cti.database.user_db.find_line_context')
    def test_get_context_no_line(self, mock_get_context):
        context = 'default'
        user_id = '206'
        self._userlist.keeplist[user_id] = {
        }
        mock_get_context.return_value = context

        self.dao.get_line = Mock(side_effect=NoSuchLineException())

        result = self.dao.get_context(user_id)

        self.assertEqual(result, context)

    def test_get_line_no_linelist_field(self):
        # Happens when the CTI server is starting
        context = 'default'
        user_id = '206'
        line_id = '607'
        self._phonelist.keeplist[line_id] = {
            'context': context,
            'protocol': 'sip',
            'number': '1234',
            'identity': 'sip/a1b2c3',
            'initialized': False,
            'allowtransfer': True
        }
        self._userlist.keeplist[user_id] = {
        }

        self.assertRaises(NoSuchLineException, self.dao.get_line, user_id)

    def test_get_line_user_not_exist(self):
        user_id = '206'
        line_id = '607'
        self._phonelist.keeplist[line_id] = {
            'context': 'default',
            'protocol': 'sip',
            'number': '1234',
            'identity': 'sip/a1b2c3',
            'initialized': False,
            'allowtransfer': True
        }
        self._userlist.keeplist = {}

        self.assertRaises(NoSuchUserException, self.dao.get_line, user_id)

    def test_get_line_line_not_exist(self):
        user_id = '206'
        line_id = '607'
        self._phonelist.keeplist = {}
        self._userlist.keeplist[user_id] = {
            'linelist': [line_id]
        }

        self.assertRaises(NoSuchLineException, self.dao.get_line, user_id)

    def test_get_cti_profile_id(self):
        user_id = '206'
        cti_profile_id = 4
        self._userlist.keeplist[user_id] = {
            'cti_profile_id': cti_profile_id
        }

        result = self.dao.get_cti_profile_id(user_id)

        self.assertEqual(result, cti_profile_id)

    def test_agent_id(self):
        user_id = '206'
        agent_id = 4
        self._userlist.keeplist[user_id] = {
            'agentid': agent_id,
        }

        result = self.dao.get_agent_id(user_id)

        self.assertEqual(result, agent_id)

    def test_agent_id_not_found(self):
        result = self.dao.get_agent_id('206')

        self.assertEqual(result, None)
