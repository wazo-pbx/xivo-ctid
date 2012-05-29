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
# contracted with Pro-formatique SARL. See the LICENSE file at top of the
# source tree or delivered in the installable package in which XiVO CTI Server
# is distributed for more details.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from xivo_cti.dao.tests import test_dao
from xivo_cti.dao.alchemy import dbconnection
from xivo_cti.dao.alchemy.userfeatures import UserFeatures
from xivo_cti.dao.userfeaturesdao import UserFeaturesDAO
from tests.mock import Mock
from xivo_cti.innerdata import Safe
from xivo_cti.lists.cti_userlist import UserList
import time


class TestUserFeaturesDAO(test_dao.DAOTestCase):

    required_tables = [UserFeatures.__table__]

    def setUp(self):
        db_connection_pool = dbconnection.DBConnectionPool(dbconnection.DBConnection)
        dbconnection.register_db_connection_pool(db_connection_pool)

        uri = 'postgresql://asterisk:asterisk@localhost/asterisktest'
        dbconnection.add_connection_as(uri, 'asterisk')
        connection = dbconnection.get_connection('asterisk')

        self.cleanTables()

        self.session = connection.get_session()

        self.session.commit()

        self._innerdata = Mock(Safe)
        self._userlist = Mock(UserList)
        self._userlist.keeplist = {}
        self._innerdata.xod_config = {'users': self._userlist}

        self.dao = UserFeaturesDAO(self.session)

    def tearDown(self):
        dbconnection.unregister_db_connection_pool()

    def test_get_one_result(self):
        user_id = self._insert_user('first')

        user = self.dao.get(user_id)

        self.assertEqual(user.id, user_id)

    def test_get_string_id(self):
        user_id = self._insert_user('first')

        user = self.dao.get(str(user_id))

        self.assertEqual(user.id, user_id)

    def test_get_no_result(self):
        self.assertRaises(LookupError, lambda: self.dao.get(1))

    def test_set_dnd(self):
        user_id = self._insert_user_dnd_not_set()
        dao = UserFeaturesDAO(self.session)
        dao._innerdata = self._innerdata

        dao.enable_dnd(user_id)

        self._check_dnd_is_set(user_id)

    def test_unset_dnd(self):
        user_id = self._insert_user_dnd_set()
        dao = UserFeaturesDAO(self.session)
        dao._innerdata = self._innerdata

        dao.disable_dnd(user_id)

        self._check_dnd_is_not_set(user_id)
        self._check_dnd_is_not_set_in_inner_data(user_id)

    def _insert_user(self, firstname):
        user = UserFeatures()
        user.firstname = firstname
        self.session.add(user)
        self.session.commit()
        return user.id

    def _insert_user_dnd_set(self):
        user_features = UserFeatures()
        user_features.enablednd = 1
        user_features.firstname = 'firstname_test'
        self.session.add(user_features)
        self.session.commit()
        user_id = user_features.id
        self._userlist.keeplist[user_id] = {'enablednd': True}
        return user_id

    def _insert_user_dnd_not_set(self):
        user_features = UserFeatures()
        user_features.enablednd = 0
        user_features.firstname = 'firstname_dnd not set'
        self.session.add(user_features)
        self.session.commit()
        user_id = user_features.id
        self._userlist.keeplist[user_id] = {'enablednd': False}
        return user_id

    def _check_dnd_is_set(self, user_id):
        user_features = (self.session.query(UserFeatures)
                         .filter(UserFeatures.id == user_id))[0]
        self.assertTrue(self._userlist.keeplist[user_id]['enablednd'])
        self.assertTrue(user_features.enablednd)

    def _check_dnd_is_not_set(self, user_id):
        user_features = (self.session.query(UserFeatures)
                         .filter(UserFeatures.id == user_id))[0]
        self.assertFalse(user_features.enablednd)

    def _check_dnd_is_not_set_in_inner_data(self, user_id):
        self.assertFalse(self._userlist.keeplist[user_id]['enablednd'])

    def test_enable_filter(self):
        user_id = self._insert_user_with_filter(0)
        dao = UserFeaturesDAO(self.session)
        dao._innerdata = self._innerdata

        dao.enable_filter(user_id)

        self._check_filter_in_db(user_id, 1)
        self._check_filter_in_inner_data(user_id, 1)

    def test_disable_filter(self):
        user_id = self._insert_user_with_filter(1)
        dao = UserFeaturesDAO(self.session)
        dao._innerdata = self._innerdata

        dao.disable_filter(user_id)

        self._check_filter_in_db(user_id, 0)
        self._check_filter_in_inner_data(user_id, 0)

    def _insert_user_with_filter(self, filter_status):
        user_features = UserFeatures()
        user_features.incallfilter = filter_status
        user_features.firstname = 'firstname_filter not set'
        self.session.add(user_features)
        self.session.commit()
        user_id = user_features.id
        self._userlist.keeplist[user_id] = {'incallfilter': False}
        return user_id

    def _check_filter_in_db(self, user_id, value):
        user_features = (self.session.query(UserFeatures)
                         .filter(UserFeatures.id == user_id))[0]
        self.assertEquals(user_features.incallfilter, value)

    def _check_filter_in_inner_data(self, user_id, value):
        if value == 0:
            self.assertFalse(self._userlist.keeplist[user_id]['incallfilter'], 'inner data not updated for filter')
        elif value == 1:
            self.assertTrue(self._userlist.keeplist[user_id]['incallfilter'], 'inner data not updated for filter')

    def test_enable_unconditional_fwd(self):
        destination = '765'
        user_id = self._insert_user_with_unconditional_fwd(destination, 0)
        dao = UserFeaturesDAO(self.session)
        dao._innerdata = self._innerdata

        dao.enable_unconditional_fwd(user_id, destination)

        self._check_unconditional_fwd_in_db(user_id, 1)
        self._check_unconditional_fwd_in_inner_data(user_id, 1)
        self._check_unconditional_dest_in_db(user_id, destination)
        self._check_unconditional_dest_in_inner_data(user_id, destination)

    def _insert_user_with_unconditional_fwd(self, destination, enabled):
        user_features = UserFeatures()
        user_features.enableunc = enabled
        user_features.destunc = destination
        user_features.firstname = 'firstname_unconditional_fwd'
        self.session.add(user_features)
        self.session.commit()
        user_id = user_features.id
        self._userlist.keeplist[user_id] = {'enableunc': enabled == 1,
                                            'destunc': destination}
        return user_id

    def _check_unconditional_fwd_in_db(self, user_id, value):
        user_features = (self.session.query(UserFeatures)
                         .filter(UserFeatures.id == user_id))[0]
        self.assertEquals(user_features.enableunc, value)

    def _check_unconditional_fwd_in_inner_data(self, user_id, value):
        self.assertEqual(self._userlist.keeplist[user_id]['enableunc'], value == 1)

    def test_unconditional_fwd_disabled(self):
        destination = '4321'
        user_id = self._insert_user_with_unconditional_fwd('', 0)
        dao = UserFeaturesDAO(self.session)
        dao._innerdata = self._innerdata

        dao.disable_unconditional_fwd(user_id, destination)

        self._check_unconditional_fwd_in_db(user_id, 0)
        self._check_unconditional_fwd_in_inner_data(user_id, 0)
        self._check_unconditional_dest_in_db(user_id, destination)
        self._check_unconditional_dest_in_inner_data(user_id, destination)

    def _check_unconditional_dest_in_inner_data(self, user_id, destination):
        self.assertEqual(self._userlist.keeplist[user_id]['destunc'], destination, 'inner data not updated for unconditional destination')

    def _check_unconditional_dest_in_db(self, user_id, destination):
        user_features = (self.session.query(UserFeatures)
                         .filter(UserFeatures.id == user_id))[0]
        self.assertEquals(user_features.destunc, destination)

    def test_rna_fwd_enabled(self):
        destination = '4321'
        user_id = self._insert_user_with_rna_fwd('', 1)
        dao = UserFeaturesDAO(self.session)
        dao._innerdata = self._innerdata

        dao.enable_rna_fwd(user_id, destination)

        self._check_rna_fwd_in_db(user_id, 1)
        self._check_rna_fwd_in_inner_data(user_id, 1)
        self._check_rna_dest_in_db(user_id, destination)
        self._check_rna_dest_in_inner_data(user_id, destination)

    def test_rna_fwd_disabled(self):
        destination = '4325'
        user_id = self._insert_user_with_rna_fwd('', 0)
        dao = UserFeaturesDAO(self.session)
        dao._innerdata = self._innerdata

        dao.disable_rna_fwd(user_id, destination)

        self._check_rna_fwd_in_db(user_id, 0)
        self._check_rna_fwd_in_inner_data(user_id, 0)
        self._check_rna_dest_in_db(user_id, destination)
        self._check_rna_dest_in_inner_data(user_id, destination)

    def _insert_user_with_rna_fwd(self, destination, enabled):
        user_features = UserFeatures()
        user_features.enablerna = enabled
        user_features.destrna = destination
        user_features.firstname = 'firstname_rna_fwd'
        self.session.add(user_features)
        self.session.commit()
        user_id = user_features.id
        self._userlist.keeplist[user_id] = {'enablerna': enabled == 1,
                                            'destrna': destination}
        return user_id

    def _check_rna_dest_in_db(self, user_id, destination):
        user_features = (self.session.query(UserFeatures)
                         .filter(UserFeatures.id == user_id))[0]
        self.assertEquals(user_features.destrna, destination)

    def _check_rna_dest_in_inner_data(self, user_id, destination):
        self.assertEqual(self._userlist.keeplist[user_id]['destrna'], destination, 'inner data not updated for rna destination')

    def _check_rna_fwd_in_inner_data(self, user_id, value):
        self.assertEqual(self._userlist.keeplist[user_id]['enablerna'], value == 1)

    def _check_rna_fwd_in_db(self, user_id, value):
        user_features = (self.session.query(UserFeatures)
                         .filter(UserFeatures.id == user_id))[0]
        self.assertEquals(user_features.enablerna, value)

    def test_busy_fwd_disabled(self):
        destination = '435'
        user_id = self._insert_user_with_busy_fwd('', 0)
        dao = UserFeaturesDAO(self.session)
        dao._innerdata = self._innerdata

        dao.disable_busy_fwd(user_id, destination)

        self._check_busy_fwd_in_db(user_id, 0)
        self._check_busy_fwd_in_inner_data(user_id, 0)
        self._check_busy_dest_in_db(user_id, destination)
        self._check_busy_dest_in_inner_data(user_id, destination)

    def test_busy_fwd_enabled(self):
        destination = '435'
        user_id = self._insert_user_with_busy_fwd('', 1)
        dao = UserFeaturesDAO(self.session)
        dao._innerdata = self._innerdata

        dao.enable_busy_fwd(user_id, destination)

        self._check_busy_fwd_in_db(user_id, 1)
        self._check_busy_fwd_in_inner_data(user_id, 1)
        self._check_busy_dest_in_db(user_id, destination)
        self._check_busy_dest_in_inner_data(user_id, destination)

    def test_find_by_agent_id(self):
        agent_id = 5
        user = UserFeatures()

        user.firstname = 'test_agent'
        user.agentid = agent_id

        self.session.add(user)
        self.session.commit()

        dao = UserFeaturesDAO(self.session)

        user_ids = dao.find_by_agent_id(agent_id)

        self.assertEqual(user_ids[0], user.id)

    def test_agent_id(self):
        agent_id = 5
        user = UserFeatures()

        user.firstname = 'test_agent'
        user.agentid = agent_id

        self.session.add(user)
        self.session.commit()

        dao = UserFeaturesDAO(self.session)

        res = dao.agent_id(user.id)

        self.assertEqual(res, agent_id)

    def test_agent_id_no_agent(self):
        user = UserFeatures()

        user.firstname = 'test_agent'

        self.session.add(user)
        self.session.commit()

        dao = UserFeaturesDAO(self.session)

        res = dao.agent_id(user.id)

        self.assertEqual(res, None)

    def _insert_user_with_busy_fwd(self, destination, enabled):
        user_features = UserFeatures()
        user_features.enablebusy = enabled
        user_features.destbusy = destination
        user_features.firstname = 'firstname_busy_fwd'
        self.session.add(user_features)
        self.session.commit()
        user_id = user_features.id
        self._userlist.keeplist[user_id] = {'enablebusy': enabled == 1,
                                            'destbusy': destination}
        return user_id

    def _check_busy_fwd_in_db(self, user_id, value):
        user_features = (self.session.query(UserFeatures)
                         .filter(UserFeatures.id == user_id))[0]
        self.assertEquals(user_features.enablebusy, value)

    def _check_busy_fwd_in_inner_data(self, user_id, value):
        self.assertEqual(self._userlist.keeplist[user_id]['enablebusy'], value == 1)

    def _check_busy_dest_in_db(self, user_id, destination):
        user_features = (self.session.query(UserFeatures)
                         .filter(UserFeatures.id == user_id))[0]
        self.assertEquals(user_features.destbusy, destination, 'Destination not updated')

    def _check_busy_dest_in_inner_data(self, user_id, destination):
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

    def test_is_agent_yes(self):
        agent_id = 5
        user = UserFeatures()

        user.firstname = 'test_agent'
        user.agentid = agent_id

        self.session.add(user)
        self.session.commit()

        result = self.dao.is_agent(user.id)

        self.assertEqual(result, True)

    def test_is_agent_no(self):
        user = UserFeatures()

        user.firstname = 'test_agent'

        self.session.add(user)
        self.session.commit()

        result = self.dao.is_agent(user.id)

        self.assertEqual(result, False)

    def test_get_profile(self):
        expected_user_profile = 'client'
        user = UserFeatures()
        user.firstname = 'test_agent'
        user.profileclient = 'client'

        self.session.add(user)
        self.session.commit()

        result = self.dao.get_profile(user.id)

        self.assertEqual(result, expected_user_profile)
