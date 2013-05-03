# -*- coding: utf-8 -*-

# Copyright (C) 2013 Avencall
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

from mock import Mock, patch
from xivo_cti.cti_command import Command
from xivo_cti.statistics.queue_statistics_manager import QueueStatisticsManager
from xivo_cti.statistics.queue_statistics_encoder import QueueStatisticsEncoder
from xivo_cti.innerdata import Safe
from xivo_cti.ctiserver import CTIServer


class Test(unittest.TestCase):

    features_return_success = {'status': 'OK'}

    def setUp(self):
        self._ctiserver = Mock(CTIServer)
        self._innerdata = Mock(Safe)
        self.conn = Mock()
        self.conn.requester = ('test_requester', 1)
        self.conn._ctiserver = self._ctiserver
        self._ctiserver.safe = self._innerdata

    @patch('xivo_cti.ioc.context.context.get', Mock())
    def test_regcommand_getqueuesstats_no_result(self):
        message = {}
        cti_command = Command(self.conn, message)
        self.assertEqual(cti_command.regcommand_getqueuesstats(), {},
                         'Default return an empty dict')

    @patch('xivo_cti.dao.queue.get_name_from_id')
    @patch('xivo_cti.ioc.context.context.get', Mock())
    def test_regcommand_getqueuesstats_one_queue(self, mock_get_name_from_id):
        message = {"class": "getqueuesstats",
                   "commandid": 1234,
                   "on": {"3": {"window": "3600", "xqos": "60"}}}
        queueStatistics = Mock(QueueStatisticsManager)
        encoder = Mock(QueueStatisticsEncoder)
        cti_command = Command(self.conn, message)
        cti_command._queue_statistics_manager = queueStatistics
        cti_command._queue_statistics_encoder = encoder
        mock_get_name_from_id.return_value = 'service'

        queueStatistics.get_statistics.return_value = queueStatistics
        statisticsToEncode = {'3': queueStatistics}

        encoder.encode.return_value = {'return value': {'value1': 'first stat'}}

        reply = cti_command.regcommand_getqueuesstats()
        self.assertEqual(reply, {'return value': {'value1': 'first stat'}})

        queueStatistics.get_statistics.assert_called_with('service', 60, 3600)
        encoder.encode.assert_called_with(statisticsToEncode)

    @patch('xivo_cti.ioc.context.context.get', Mock())
    def test_regcommand_login_pass_no_session(self):
        message = {"class": "login_pass",
                   "hashedpassword": "abcd"}
        cti_command = Command(self.conn, message)
        cti_command.ipbxid = 1
        cti_command.userid = 2
        self.assertEquals("login_password", cti_command.regcommand_login_pass())

    @patch('xivo_cti.ioc.context.context.get', Mock())
    def test_regcommand_login_pass_wrong_password(self):
        message = {"class": "login_pass",
                   "hashedpassword": "abcd"}
        self.conn.connection_details = {'prelogin': {'sessionid': '1234'}}
        cti_command = Command(self.conn, message)
        cti_command.ipbxid = 1
        cti_command.userid = 2
        self._ctiserver.safe.user_get_hashed_password.return_value = "efgh"
        self.assertEquals("login_password", cti_command.regcommand_login_pass())

    @patch('xivo_cti.ioc.context.context.get', Mock())
    @patch('xivo_dao.user_dao.get_profile')
    def test_regcommand_login_pass_no_profile(self, mock_get_profile):
        message = {"class": "login_pass",
                   "hashedpassword": "abcd"}
        self.conn.connection_details = {'prelogin': {'sessionid': '1234'}}
        cti_command = Command(self.conn, message)
        cti_command.ipbxid = 1
        cti_command.userid = 2
        self._ctiserver.safe.user_get_hashed_password.return_value = "abcd"
        mock_get_profile.return_value = None
        self.assertEquals("capaid_undefined", cti_command.regcommand_login_pass())

    @patch('xivo_cti.ioc.context.context.get', Mock())
    @patch('xivo_dao.user_dao.get_profile')
    def test_regcommand_login_pass_success(self, mock_get_profile):
        message = {"class": "login_pass",
                   "hashedpassword": "abcd"}
        self.conn.connection_details = {'prelogin': {'sessionid': '1234'}}
        cti_command = Command(self.conn, message)
        cti_command.ipbxid = 1
        cti_command.userid = 2
        self._ctiserver.safe.user_get_hashed_password.return_value = "abcd"
        mock_get_profile.return_value = 3
        self.assertEquals({'capalist': [3]}, cti_command.regcommand_login_pass())
