# -*- coding: utf-8 -*-

# Copyright (C) 2007-2013 Avencall
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

import unittest

from hamcrest import *
from mock import Mock
from xivo_cti import dao
from xivo_cti.scheduler import Scheduler
from xivo_cti.services.agent.status import AgentStatus
from xivo_cti.services.agent.availability_updater import AgentAvailabilityUpdater
from xivo_cti.services.agent.availability_notifier import AgentAvailabilityNotifier
from xivo_cti.services.agent import availability_updater as agent_availability_updater
from xivo_cti.dao.agent_dao import AgentDAO
from xivo_cti.dao.innerdata_dao import InnerdataDAO
from xivo_cti.exception import NoSuchAgentException


class TestAgentAvailabilityUpdater(unittest.TestCase):

    def setUp(self):
        dao.agent = Mock(AgentDAO)
        self.agent_availability_updater = AgentAvailabilityUpdater(Mock(AgentAvailabilityNotifier), Mock(Scheduler))
        self.agent_availability_updater.dao.innerdata = Mock(InnerdataDAO)

    def test_parse_ami_login(self):
        agent_id = 12
        ami_event = {'AgentID': agent_id,
                     'Event': 'UserEvent',
                     'UserEvent': 'AgentLogin'}
        dao.agent.get_id_from_number.return_value = agent_id
        mock_agent_availability_updater = Mock(AgentAvailabilityUpdater)

        agent_availability_updater.parse_ami_login(ami_event, mock_agent_availability_updater)

        mock_agent_availability_updater.agent_logged_in.assert_called_with(agent_id)

    def test_parse_ami_logout(self):
        agent_id = 12
        ami_event = {'AgentID': agent_id,
                     'Event': 'UserEvent',
                     'UserEvent': 'AgentLogoff'}
        dao.agent.get_id_from_number.return_value = agent_id
        mock_agent_availability_updater = Mock(AgentAvailabilityUpdater)

        agent_availability_updater.parse_ami_logout(ami_event, mock_agent_availability_updater)

        mock_agent_availability_updater.agent_logged_out.assert_called_with(agent_id)

    def test_parse_ami_answered(self):
        agent_id = 12
        ami_event = {'MemberName': 'Agent/1234',
                     'Event': 'AgentConnect'}
        dao.agent.get_id_from_interface.return_value = agent_id
        mock_agent_availability_updater = Mock(AgentAvailabilityUpdater)

        agent_availability_updater.parse_ami_answered(ami_event, mock_agent_availability_updater)

        mock_agent_availability_updater.agent_answered.assert_called_with(agent_id)

    def test_parse_ami_answered_not_an_agent(self):
        ami_event = {'MemberName': 'SIP/abcdef',
                     'Event': 'AgentConnect'}
        dao.agent.get_id_from_interface.side_effect = ValueError()
        mock_agent_availability_updater = Mock(AgentAvailabilityUpdater)

        agent_availability_updater.parse_ami_answered(ami_event, mock_agent_availability_updater)

        self.assertFalse(mock_agent_availability_updater.agent_answered.called)

    def test_parse_ami_call_completed(self):
        agent_id = 12
        wrapup_time = 15

        ami_event = {'MemberName': 'Agent/1234',
                     'Event': 'AgentComplete',
                     'WrapupTime': str(wrapup_time)}
        dao.agent.get_id_from_interface.return_value = agent_id
        mock_agent_availability_updater = Mock(AgentAvailabilityUpdater)

        agent_availability_updater.parse_ami_call_completed(ami_event, mock_agent_availability_updater)

        mock_agent_availability_updater.agent_call_completed.assert_called_with(agent_id, wrapup_time)

    def test_parse_ami_call_completed_not_an_agent(self):
        ami_event = {'MemberName': 'SIP/abcdef',
                     'Event': 'AgentComplete',
                     'WrapupTime': '15'}
        dao.agent.get_id_from_interface.side_effect = ValueError()
        mock_agent_availability_updater = Mock(AgentAvailabilityUpdater)

        agent_availability_updater.parse_ami_call_completed(ami_event, mock_agent_availability_updater)

        self.assertFalse(mock_agent_availability_updater.agent_call_completed.called)

    def test_parse_ami_paused_partially(self):
        agent_id = 12
        ami_event = {'MemberName': 'Agent/1234',
                     'Event': 'QueueMemberPaused',
                     'Queue': 'q01',
                     'Paused': '1'}
        dao.agent.get_id_from_interface.return_value = agent_id
        dao.agent.is_completely_paused.return_value = False
        mock_agent_availability_updater = Mock(AgentAvailabilityUpdater)

        agent_availability_updater.parse_ami_paused(ami_event, mock_agent_availability_updater)

        self.assertEqual(mock_agent_availability_updater.agent_paused_all.call_count, 0)

    def test_parse_ami_paused_completely(self):
        agent_id = 12
        ami_event = {'MemberName': 'Agent/1234',
                     'Event': 'QueueMemberPaused',
                     'Queue': 'q01',
                     'Paused': '1'}
        dao.agent.get_id_from_interface.return_value = agent_id
        dao.agent.is_completely_paused.return_value = True
        mock_agent_availability_updater = Mock(AgentAvailabilityUpdater)

        agent_availability_updater.parse_ami_paused(ami_event, mock_agent_availability_updater)

        mock_agent_availability_updater.agent_paused_all.assert_called_once_with(agent_id)

    def test_parse_ami_paused_not_an_agent(self):
        ami_event = {'MemberName': 'SIP/abcdef',
                     'Event': 'QueueMemberPaused',
                     'Queue': 'q01',
                     'Paused': '1'}
        dao.agent.get_id_from_interface.side_effect = ValueError()
        mock_agent_availability_updater = Mock(AgentAvailabilityUpdater)

        agent_availability_updater.parse_ami_paused(ami_event, mock_agent_availability_updater)

        self.assertFalse(mock_agent_availability_updater.agent_paused_all.called)
        self.assertFalse(mock_agent_availability_updater.agent_unpaused.called)

    def test_parse_ami_unpaused(self):
        agent_id = 12
        ami_event = {'MemberName': 'Agent/1234',
                     'Event': 'QueueMemberPaused',
                     'Queue': 'q01',
                     'Paused': '0'}
        dao.agent.get_id_from_interface.return_value = agent_id
        mock_agent_availability_updater = Mock(AgentAvailabilityUpdater)

        agent_availability_updater.parse_ami_paused(ami_event, mock_agent_availability_updater)

        mock_agent_availability_updater.agent_unpaused.assert_called_once_with(agent_id)

    def test_agent_logged_in(self):
        dao.agent = Mock(AgentDAO)
        dao.agent.is_completely_paused.return_value = False

        agent_id = 12

        self.agent_availability_updater.agent_logged_in(agent_id)

        self.agent_availability_updater.dao.innerdata.set_agent_availability.assert_called_once_with(
            agent_id,
            AgentStatus.available
        )
        self.agent_availability_updater.notifier.notify.assert_called_once_with(agent_id)

    def test_agent_logged_in_paused(self):
        dao.agent = Mock(AgentDAO)
        dao.agent.is_completely_paused.return_value = True

        agent_id = 12

        self.agent_availability_updater.agent_logged_in(agent_id)

        self.agent_availability_updater.dao.innerdata.set_agent_availability.assert_called_once_with(
            agent_id,
            AgentStatus.unavailable
        )
        self.agent_availability_updater.notifier.notify.assert_called_once_with(agent_id)

    def test_agent_logged_out(self):
        agent_id = 12

        self.agent_availability_updater.agent_logged_out(agent_id)

        self.agent_availability_updater.dao.innerdata.set_agent_availability.assert_called_once_with(
            agent_id,
            AgentStatus.logged_out
        )
        self.agent_availability_updater.notifier.notify.assert_called_once_with(agent_id)

    def test_agent_logged_out_no_such_agent(self):
        agent_id = 12
        self.agent_availability_updater.dao.innerdata.set_agent_availability.side_effect = NoSuchAgentException()

        self.agent_availability_updater.agent_logged_out(agent_id)

        assert_that(self.agent_availability_updater.notifier.notify.call_count, equal_to(0), 'Notifier call count')
        self.assertEqual(self.agent_availability_updater.notifier.notify.call_count, 0)

    def test_agent_answered(self):
        agent_id = 12

        self.agent_availability_updater.agent_answered(agent_id)

        self.agent_availability_updater.dao.innerdata.set_agent_availability.assert_called_once_with(
            agent_id,
            AgentStatus.unavailable
        )
        self.agent_availability_updater.notifier.notify.assert_called_once_with(agent_id)

    def test_agent_call_completed(self):
        dao.agent = Mock(AgentDAO)
        dao.agent.is_completely_paused.return_value = False

        agent_id = 12
        wrapup_time = 25

        self.agent_availability_updater.agent_call_completed(agent_id, wrapup_time)

        self.agent_availability_updater.scheduler.schedule.assert_called_once_with(
            wrapup_time,
            self.agent_availability_updater.agent_wrapup_completed,
            agent_id
        )
        self.assertEqual(self.agent_availability_updater.dao.innerdata.set_agent_availability.call_count, 0)
        self.assertEqual(self.agent_availability_updater.notifier.notify.call_count, 0)

    def test_agent_call_completed_logged_out(self):
        dao.agent = Mock(AgentDAO)
        dao.agent.is_completely_paused.return_value = False
        dao.agent.is_logged.return_value = False

        agent_id = 12

        self.agent_availability_updater.agent_call_completed(agent_id, 0)

        self.assertEqual(self.agent_availability_updater.dao.innerdata.set_agent_availability.call_count, 0)
        self.assertEqual(self.agent_availability_updater.notifier.notify.call_count, 0)

    def test_agent_call_completed_no_wrapup_paused(self):
        dao.agent = Mock(AgentDAO)
        dao.agent.is_completely_paused.return_value = True

        agent_id = 12
        wrapup_time = 0

        self.agent_availability_updater.agent_call_completed(agent_id, wrapup_time)

        self.assertEqual(self.agent_availability_updater.scheduler.schedule.call_count, 0)
        self.assertEqual(self.agent_availability_updater.dao.innerdata.set_agent_availability.call_count, 0)
        self.assertEqual(self.agent_availability_updater.notifier.notify.call_count, 0)

    def test_agent_call_completed_no_wrapup(self):
        dao.agent = Mock(AgentDAO)
        dao.agent.is_completely_paused.return_value = False
        agent_availability_updater.scheduler = Mock(Scheduler)

        agent_id = 12
        wrapup_time = 0

        self.agent_availability_updater.agent_call_completed(agent_id, wrapup_time)

        self.assertEqual(self.agent_availability_updater.scheduler.schedule.call_count, 0)
        self.agent_availability_updater.dao.innerdata.set_agent_availability.assert_called_once_with(agent_id, AgentStatus.available)
        self.agent_availability_updater.notifier.notify.assert_called_once_with(agent_id)

    def test_agent_wrapup_completed(self):
        dao.agent = Mock(AgentDAO)
        dao.agent.is_completely_paused.return_value = False
        dao.agent.is_logged.return_value = True

        agent_id = 12

        self.agent_availability_updater.agent_wrapup_completed(agent_id)

        self.agent_availability_updater.dao.innerdata.set_agent_availability.assert_called_once_with(agent_id, AgentStatus.available)
        self.agent_availability_updater.notifier.notify.assert_called_once_with(agent_id)

    def test_agent_wrapup_completed_in_pause(self):
        dao.agent = Mock(AgentDAO)
        dao.agent.is_completely_paused.return_value = True
        dao.agent.is_logged.return_value = True

        agent_id = 12

        self.agent_availability_updater.agent_wrapup_completed(agent_id)

        self.assertEqual(self.agent_availability_updater.dao.innerdata.set_agent_availability.call_count, 0)
        self.assertEqual(self.agent_availability_updater.notifier.notify.call_count, 0)

    def test_agent_wrapup_completed_logged_out(self):
        dao.agent = Mock(AgentDAO)
        dao.agent.is_completely_paused.return_value = False
        dao.agent.is_logged.return_value = False

        agent_id = 12

        self.agent_availability_updater.agent_wrapup_completed(agent_id)

        self.assertEqual(self.agent_availability_updater.dao.innerdata.set_agent_availability.call_count, 0)
        self.assertEqual(self.agent_availability_updater.notifier.notify.call_count, 0)

    def test_agent_paused_all(self):
        dao.agent = Mock(AgentDAO)
        dao.agent.is_logged.return_value = True

        agent_id = 12

        self.agent_availability_updater.agent_paused_all(agent_id)

        self.agent_availability_updater.dao.innerdata.set_agent_availability.assert_called_once_with(agent_id, AgentStatus.unavailable)
        self.agent_availability_updater.notifier.notify.assert_called_once_with(agent_id)

    def test_agent_paused_all_while_unlogged(self):
        dao.agent = Mock(AgentDAO)
        dao.agent.is_logged.return_value = False

        agent_id = 12

        self.agent_availability_updater.agent_paused_all(agent_id)

        self.assertEqual(self.agent_availability_updater.dao.innerdata.set_agent_availability.call_count, 0)
        self.assertEqual(self.agent_availability_updater.notifier.notify.call_count, 0)

    def test_agent_unpaused(self):
        dao.agent = Mock(AgentDAO)
        dao.agent.is_logged.return_value = True
        dao.agent.on_call.return_value = False

        agent_id = 12

        self.agent_availability_updater.agent_unpaused(agent_id)

        self.agent_availability_updater.dao.innerdata.set_agent_availability.assert_called_once_with(agent_id, AgentStatus.available)
        self.agent_availability_updater.notifier.notify.assert_called_once_with(agent_id)

    def test_agent_unpaused_calling(self):
        dao.agent = Mock(AgentDAO)
        dao.agent.is_logged.return_value = True
        dao.agent.on_call.return_value = True

        agent_id = 12

        self.agent_availability_updater.agent_unpaused(agent_id)

        self.assertEqual(self.agent_availability_updater.dao.innerdata.set_agent_availability.call_count, 0)
        self.assertEqual(self.agent_availability_updater.notifier.notify.call_count, 0)

    def test_agent_unpaused_while_unlogged(self):
        dao.agent = Mock(AgentDAO)
        dao.agent.is_logged.return_value = False

        agent_id = 12

        self.agent_availability_updater.agent_unpaused(agent_id)

        self.assertEqual(self.agent_availability_updater.dao.innerdata.set_agent_availability.call_count, 0)
        self.assertEqual(self.agent_availability_updater.notifier.notify.call_count, 0)
