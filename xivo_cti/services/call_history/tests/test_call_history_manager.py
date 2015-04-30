# -*- coding: utf-8 -*-

# Copyright (C) 2013-2014 Avencall
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
from hamcrest import assert_that, same_instance
from mock import Mock, sentinel
from mock import patch
from datetime import datetime, timedelta
from xivo_cti.cti.commands.history import HistoryMode
from xivo_cti.services.call_history.manager import AllCall
from xivo_cti.services.call_history import manager as call_history_manager
from xivo_dao.data_handler.call_log.model import CallLog

mock_channels_for_phone = Mock()
mock_caller_id_by_unique_id = Mock()


class CallHistoryMgrTest(unittest.TestCase):

    def setUp(self):
        self.caller_ids = {}

        def caller_id_by_unique_id_side_effect(unique_id):
            return self.caller_ids[unique_id]
        mock_caller_id_by_unique_id.side_effect = caller_id_by_unique_id_side_effect

    def tearDown(self):
        mock_channels_for_phone.reset()
        mock_caller_id_by_unique_id.reset()

    @patch('xivo_cti.services.call_history.manager.all_calls_for_phone')
    def test_history_for_phone_all(self, all_calls):
        identifier = u'sip/abcdef'
        phone = {u'protocol': u'sip',
                 u'name': u'abcdef'}
        all_calls.return_value = sentinel.calls

        result = call_history_manager.history_for_phone(phone,
                                                        sentinel.limit)

        all_calls.assert_called_once_with(identifier, sentinel.limit)
        assert_that(result, same_instance(sentinel.calls))

    @patch('xivo_dao.data_handler.call_log.dao.find_all_history_for_phone')
    def test_all_calls_for_phone(self, mock_all_for_phone):
        now = datetime.now()
        identifier = u'sip/abcdef'
        date1 = date2 = date3 = now

        duration1 = 2
        caller_name1 = u'Foo'
        extension1 = u'123'
        mode1 = HistoryMode.answered

        duration2 = 0
        caller_name2 = u'Bar'
        extension2 = u'456'
        mode2 = HistoryMode.missed

        duration3 = 3
        caller_name3 = None
        extension3 = u'789'
        mode3 = HistoryMode.outgoing

        call_log_1 = CallLog(answered=True,
                             date=now,
                             destination_line_identity=identifier,
                             duration=timedelta(0, 2, 0),
                             source_name=u'Foo',
                             source_exten=u'123')

        call_log_2 = CallLog(answered=False,
                             date=now,
                             destination_line_identity=identifier,
                             duration=timedelta(0, 0, 0),
                             source_name=u'Bar',
                             source_exten=u'456')

        call_log_3 = CallLog(date=now,
                             destination_line_identity=None,
                             duration=timedelta(0, 3, 0),
                             destination_exten=u'789')

        returned_call_logs = [call_log_1, call_log_2, call_log_3]

        expected_all_calls = [AllCall(date1, duration1, caller_name1, extension1, mode1),
                              AllCall(date2, duration2, caller_name2, extension2, mode2),
                              AllCall(date3, duration3, caller_name3, extension3, mode3)]

        mock_all_for_phone.return_value = returned_call_logs

        all_calls = call_history_manager.all_calls_for_phone(identifier, 3)

        mock_all_for_phone.assert_called_once_with(identifier, 3)
        self.assertEqual(expected_all_calls, all_calls)
