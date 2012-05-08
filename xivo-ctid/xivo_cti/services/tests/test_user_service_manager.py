#!/usr/bin/python
# vim: set fileencoding=utf-8 :

# Copyright (C) 2007-2011  Avencall
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

import unittest

from tests.mock import Mock
from xivo_cti.dao.userfeaturesdao import UserFeaturesDAO
from xivo_cti.services.user_service_notifier import UserServiceNotifier
from xivo_cti.services.user_service_manager import UserServiceManager
from xivo_cti.funckey.funckey_manager import FunckeyManager
from xivo_cti.dao.phonefunckeydao import PhoneFunckeyDAO
from xivo_cti.services.presence_service_executor import PresenceServiceExecutor
from xivo_cti.services.agent_service_manager import AgentServiceManager
from xivo_cti.services.presence_service_manager import PresenceServiceManager
from xivo_cti.dao.linefeaturesdao import LineFeaturesDAO
from xivo_cti.dao.alchemy import dbconnection
from xivo_cti.dao.alchemy.linefeatures import LineFeatures
from xivo_cti.dao.alchemy.userfeatures import UserFeatures
from xivo_cti.dao.alchemy.base import Base

class TestUserServiceManager(unittest.TestCase):

    def setUp(self):
        db_connection_pool = dbconnection.DBConnectionPool(dbconnection.DBConnection)
        dbconnection.register_db_connection_pool(db_connection_pool)

        uri = 'postgresql://asterisk:asterisk@localhost/asterisktest'
        dbconnection.add_connection_as(uri, 'asterisk')
        connection = dbconnection.get_connection('asterisk')

        self.session = connection.get_session()

        Base.metadata.drop_all(connection.get_engine(), [LineFeatures.__table__])
        Base.metadata.create_all(connection.get_engine(), [LineFeatures.__table__])
        Base.metadata.drop_all(connection.get_engine(), [UserFeatures.__table__])
        Base.metadata.create_all(connection.get_engine(), [UserFeatures.__table__])

        self.user_service_manager = UserServiceManager()
        self.user_features_dao = Mock(UserFeaturesDAO)
        self.line_features_dao = Mock(LineFeaturesDAO)
        self.phone_funckey_dao = Mock(PhoneFunckeyDAO)
        self.user_service_manager.user_features_dao = self.user_features_dao
        self.user_service_manager.phone_funckey_dao = self.phone_funckey_dao
        self.funckey_manager = Mock(FunckeyManager)
        self.user_service_notifier = Mock(UserServiceNotifier)
        self.user_service_manager.user_service_notifier = self.user_service_notifier
        self.user_service_manager.funckey_manager = self.funckey_manager
        self.user_service_manager.line_features_dao = self.line_features_dao

    def tearDown(self):
        dbconnection.unregister_db_connection_pool()

    def test_enable_dnd(self):
        user_id = 123

        self.user_service_manager.enable_dnd(user_id)

        self.user_features_dao.enable_dnd.assert_called_once_with(user_id)
        self.user_service_notifier.dnd_enabled.assert_called_once_with(user_id)
        self.funckey_manager.dnd_in_use.assert_called_once_with(user_id, True)

    def test_disable_dnd(self):
        user_id = 241

        self.user_service_manager.disable_dnd(user_id)

        self.user_features_dao.disable_dnd.assert_called_once_with(user_id)
        self.user_service_notifier.dnd_disabled.assert_called_once_with(user_id)
        self.funckey_manager.dnd_in_use.assert_called_once_with(user_id, False)

    def test_set_dnd(self):
        old_enable, self.user_service_manager.enable_dnd = self.user_service_manager.enable_dnd, Mock()
        old_disable, self.user_service_manager.disable_dnd = self.user_service_manager.disable_dnd, Mock()

        user_id = 555

        self.user_service_manager.set_dnd(user_id, True)

        self.user_service_manager.enable_dnd.assert_called_once_with(user_id)

        self.user_service_manager.set_dnd(user_id, False)

        self.user_service_manager.disable_dnd.assert_called_once_with(user_id)

        self.user_service_manager.enable_dnd = old_enable
        self.user_service_manager.disable_dnd = old_disable

    def test_enable_filter(self):
        user_id = 789

        self.user_service_manager.enable_filter(user_id)

        self.user_features_dao.enable_filter.assert_called_once_with(user_id)
        self.user_service_notifier.filter_enabled.assert_called_once_with(user_id)
        self.funckey_manager.call_filter_in_use.assert_called_once_with(user_id, True)

    def test_disable_filter(self):
        user_id = 834

        self.user_service_manager.disable_filter(user_id)

        self.user_features_dao.disable_filter.assert_called_once_with(user_id)
        self.user_service_notifier.filter_disabled.assert_called_once_with(user_id)
        self.funckey_manager.call_filter_in_use.assert_called_once_with(user_id, False)

    def test_enable_unconditional_fwd(self):
        user_id = 543321
        destination = '234'
        self.user_service_manager.phone_funckey_dao.get_dest_unc.return_value = [destination]

        self.user_service_manager.enable_unconditional_fwd(user_id, destination)

        self.user_features_dao.enable_unconditional_fwd.assert_called_once_with(user_id, destination)
        self.user_service_notifier.unconditional_fwd_enabled.assert_called_once_with(user_id, destination)
        self.funckey_manager.unconditional_fwd_in_use.assert_called_once_with(user_id, destination, True)

    def test_disable_unconditional_fwd(self):
        user_id = 543
        destination = '1234'
        fwd_key_dest = '102'
        self.phone_funckey_dao.get_dest_unc.return_value = [fwd_key_dest]

        self.user_service_manager.disable_unconditional_fwd(user_id, destination)

        self.user_features_dao.disable_unconditional_fwd.assert_called_once_with(user_id, destination)
        self.user_service_notifier.unconditional_fwd_disabled.assert_called_once_with(user_id, destination)
        self.funckey_manager.disable_all_unconditional_fwd.assert_called_once_with(user_id)

    def test_enable_rna_fwd(self):
        user_id = 2345
        destination = '3456'
        self.user_service_manager.phone_funckey_dao.get_dest_rna.return_value = [destination]

        self.user_service_manager.enable_rna_fwd(user_id, destination)

        self.user_features_dao.enable_rna_fwd.assert_called_once_with(user_id, destination)
        self.user_service_notifier.rna_fwd_enabled.assert_called_once_with(user_id, destination)
        self.funckey_manager.disable_all_rna_fwd.assert_called_once_with(user_id)
        self.funckey_manager.rna_fwd_in_use.assert_called_once_with(user_id, destination, True)

    def test_disable_rna_fwd(self):
        user_id = 2345
        destination = '3456'
        fwd_key_dest = '987'
        self.phone_funckey_dao.get_dest_rna.return_value = [fwd_key_dest]

        self.user_service_manager.disable_rna_fwd(user_id, destination)

        self.user_features_dao.disable_rna_fwd.assert_called_once_with(user_id, destination)
        self.user_service_notifier.rna_fwd_disabled.assert_called_once_with(user_id, destination)
        self.funckey_manager.disable_all_rna_fwd.assert_called_once_with(user_id)

    def test_enable_busy_fwd(self):
        user_id = 2345
        destination = '3456'
        fwd_key_dest = '3456'
        self.phone_funckey_dao.get_dest_busy.return_value = [fwd_key_dest]

        self.user_service_manager.enable_busy_fwd(user_id, destination)

        self.user_features_dao.enable_busy_fwd.assert_called_once_with(user_id, destination)
        self.user_service_notifier.busy_fwd_enabled.assert_called_once_with(user_id, destination)
        self.funckey_manager.disable_all_busy_fwd.assert_called_once_with(user_id)
        self.funckey_manager.busy_fwd_in_use.assert_called_once_with(user_id, destination, True)

    def test_disable_busy_fwd(self):
        user_id = 2345
        destination = '3456'
        fwd_key_dest = '666'
        self.phone_funckey_dao.get_dest_busy.return_value = [fwd_key_dest]

        self.user_service_manager.disable_busy_fwd(user_id, destination)

        self.user_features_dao.disable_busy_fwd.assert_called_once_with(user_id, destination)
        self.user_service_notifier.busy_fwd_disabled.assert_called_once_with(user_id, destination)
        self.funckey_manager.disable_all_busy_fwd.assert_called_once_with(user_id)

    def test_enable_busy_fwd_not_funckey(self):
        user_id = 2345
        destination = '3456'
        fwd_key_dest = '666'
        self.phone_funckey_dao.get_dest_busy.return_value = [fwd_key_dest]

        self.user_service_manager.enable_busy_fwd(user_id, destination)

        self.user_features_dao.enable_busy_fwd.assert_called_once_with(user_id, destination)
        self.user_service_notifier.busy_fwd_enabled.assert_called_once_with(user_id, destination)

    def test_disconnect(self):
        user_id = 95
        self.user_service_manager.user_features_dao = Mock(UserFeaturesDAO)
        self.user_service_manager.set_presence = Mock()

        self.user_service_manager.disconnect(user_id)

        self.user_service_manager.user_features_dao.disconnect.assert_called_once_with(user_id)
        self.user_service_manager.set_presence.assert_called_once_with(user_id, 'disconnected')

    def test_set_valid_presence_no_agent(self):
        user_id = 95
        presence = 'disconnected'
        expected_presence = 'disconnected'
        user_profile = 'client'
        self.user_service_manager.user_features_dao = Mock(UserFeaturesDAO)
        self.user_service_manager.user_features_dao.get_profile.return_value = user_profile
        self.user_service_manager.user_features_dao.is_agent.return_value = False
        self.user_service_manager.presence_service_manager = Mock(PresenceServiceManager)
        self.user_service_manager.presence_service_manager.is_valid_presence.return_value = True
        self.user_service_manager.presence_service_executor = Mock(PresenceServiceExecutor)
        self.user_service_manager.agent_service_manager = Mock(AgentServiceManager)

        self.user_service_manager.set_presence(user_id, presence)

        self.user_service_manager.presence_service_manager.is_valid_presence.assert_called_once_with(user_profile, expected_presence)
        self.user_service_manager.user_features_dao.set_presence.assert_called_once_with(user_id, expected_presence)
        self.user_service_manager.presence_service_executor.execute_actions.assert_called_once_with(user_id, expected_presence)
        self.user_service_notifier.presence_updated.assert_called_once_with(user_id, expected_presence)
        self.user_service_manager.user_features_dao.is_agent.assert_called_once_with(user_id)
        self.user_service_manager.agent_service_manager.set_presence.assert_never_called()

    def test_set_valid_presence_with_agent(self):
        user_id = 95
        expected_agent_id = 10
        presence = 'disconnected'
        expected_presence = 'disconnected'
        user_profile = 'client'
        self.user_service_manager.user_features_dao = Mock(UserFeaturesDAO)
        self.user_service_manager.user_features_dao.get_profile.return_value = user_profile
        self.user_service_manager.user_features_dao.is_agent.return_value = True
        self.user_service_manager.user_features_dao.agent_id.return_value = expected_agent_id
        self.user_service_manager.presence_service_manager = Mock(PresenceServiceManager)
        self.user_service_manager.presence_service_manager.is_valid_presence.return_value = True
        self.user_service_manager.presence_service_executor = Mock(PresenceServiceExecutor)
        self.user_service_manager.agent_service_manager = Mock(AgentServiceManager)

        self.user_service_manager.set_presence(user_id, presence)

        self.user_service_manager.presence_service_manager.is_valid_presence.assert_called_once_with(user_profile, expected_presence)
        self.user_service_manager.user_features_dao.set_presence.assert_called_once_with(user_id, expected_presence)
        self.user_service_manager.presence_service_executor.execute_actions.assert_called_once_with(user_id, expected_presence)
        self.user_service_notifier.presence_updated.assert_called_once_with(user_id, expected_presence)
        self.user_service_manager.user_features_dao.is_agent.assert_called_once_with(user_id)
        self.user_service_manager.agent_service_manager.set_presence.assert_called_once_with(expected_agent_id, expected_presence)

    def test_set_not_valid_presence(self):
        user_id = 95
        presence = 'disconnected'
        expected_presence = 'disconnected'
        user_profile = 'client'
        self.user_service_manager.user_features_dao = Mock(UserFeaturesDAO)
        self.user_service_manager.user_features_dao.get_profile.return_value = user_profile
        self.user_service_manager.presence_service_manager = Mock(PresenceServiceManager)
        self.user_service_manager.presence_service_manager.is_valid_presence.return_value = False
        self.user_service_manager.presence_service_executor = Mock(PresenceServiceExecutor)
        self.user_service_manager.agent_service_manager = Mock(AgentServiceManager)

        self.user_service_manager.set_presence(user_id, presence)

        self.user_service_manager.presence_service_manager.is_valid_presence.assert_called_once_with(user_profile, expected_presence)
        self.user_service_manager.user_features_dao.set_presence.assert_never_called()
        self.user_service_manager.presence_service_executor.assert_never_called()
        self.user_service_notifier.presence_updated.assert_never_called()
        self.user_service_manager.user_features_dao.is_agent.assert_never_called()
        self.user_service_manager.agent_service_manager.set_presence.assert_never_called()


    def _insert_user(self):
        user = UserFeatures()
        user.firstname = 'test'
        self.session.add(user)
        self.session.commit()

        return user.id

    def _insert_line_with_user(self, user_id, number, context='test_context'):
        line = LineFeatures()
        line.iduserfeatures = user_id
        line.protocolid = 1
        line.provisioningid = 0
        line.name = 'ix8pa'
        line.context = context
        line.number = number
        self.session.add(line)

        self.session.commit()

        return line

    def test_get_context(self):
        user1_id = self._insert_user()
        line1 = self._insert_line_with_user(user1_id, '100', 'context1')
        user2_id = self._insert_user()
        line2 = self._insert_line_with_user(user2_id, '101', 'context2')

        self.line_features_dao.find_context_by_user_id.side_effect = lambda x: 'context1' if x == user1_id else 'context2'

        context1 = self.user_service_manager.get_context(user1_id)
        context2 = self.user_service_manager.get_context(user2_id)

        self.assertEqual(context1, line1.context)
        self.assertEqual(context2, line2.context)
