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
from hamcrest import assert_that, contains, equal_to, same_instance
from mock import Mock, sentinel
from mock import patch
from datetime import datetime, timedelta
from xivo_cti.cti.commands.history import HistoryMode
from xivo_cti.services.call_history.manager import ReceivedCall, SentCall
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

    @patch('xivo_cti.services.call_history.manager.outgoing_calls_for_phone')
    def test_history_for_phone_outgoing(self, outgoing_calls):
        identifier = u'sip/abcdef'
        phone = {u'protocol': u'sip',
                 u'name': u'abcdef'}
        mode = HistoryMode.outgoing
        outgoing_calls.return_value = sentinel.calls

        result = call_history_manager.history_for_phone(phone,
                                                        mode,
                                                        sentinel.limit)

        outgoing_calls.assert_called_once_with(identifier, sentinel.limit)
        assert_that(result, same_instance(sentinel.calls))

    @patch('xivo_cti.services.call_history.manager.answered_calls_for_phone')
    def test_history_for_phone_answered(self, answered_calls):
        identifier = u'sip/abcdef'
        phone = {u'protocol': u'sip',
                 u'name': u'abcdef'}
        mode = HistoryMode.answered
        answered_calls.return_value = sentinel.calls

        result = call_history_manager.history_for_phone(phone,
                                                        mode,
                                                        sentinel.limit)

        answered_calls.assert_called_once_with(identifier, sentinel.limit)
        assert_that(result, same_instance(sentinel.calls))

    @patch('xivo_cti.services.call_history.manager.missed_calls_for_phone')
    def test_history_for_phone_missed(self, missed_calls):
        identifier = u'sip/abcdef'
        phone = {u'protocol': u'sip',
                 u'name': u'abcdef'}
        mode = HistoryMode.missed
        missed_calls.return_value = sentinel.calls

        result = call_history_manager.history_for_phone(phone,
                                                        mode,
                                                        sentinel.limit)

        missed_calls.assert_called_once_with(identifier, sentinel.limit)
        assert_that(result, same_instance(sentinel.calls))

    @patch('xivo_cti.services.call_history.manager.outgoing_calls_for_phone')
    @patch('xivo_cti.services.call_history.manager.answered_calls_for_phone')
    @patch('xivo_cti.services.call_history.manager.missed_calls_for_phone')
    def test_history_for_phone_unknown(self, missed_calls, answered_calls, outgoing_calls):
        phone = {u'protocol': u'sip',
                 u'name': u'abcdef'}
        mode = 'unknown'

        result = call_history_manager.history_for_phone(phone,
                                                        mode,
                                                        sentinel.limit)

        assert_that(outgoing_calls.call_count, equal_to(0))
        assert_that(answered_calls.call_count, equal_to(0))
        assert_that(missed_calls.call_count, equal_to(0))
        assert_that(result, contains())

    @patch('xivo_dao.data_handler.call_log.dao.find_all_answered_for_phone')
    def test_answered_calls_for_phone(self, mock_answered_for_phone):
        now = datetime.now()
        identifier = u'sip/abcdef'
        date1 = date2 = date3 = now
        duration1 = 1
        caller_name1 = u'"Foo" <123>'
        duration2 = 2
        caller_name2 = u'"Bar" <456>'
        duration3 = 3
        caller_name3 = u'"Man" <789>'

        call_log_1 = CallLog(date=now,
                             duration=timedelta(0, 1, 0),
                             source_name=u'Foo',
                             source_exten=u'123')

        call_log_2 = CallLog(date=now,
                             duration=timedelta(0, 2, 0),
                             source_name=u'Bar',
                             source_exten=u'456')

        returned_call_logs = [call_log_1, call_log_2]

        expected_received_calls = [ReceivedCall(date1, duration1, caller_name1),
                                   ReceivedCall(date2, duration2, caller_name2)]

        mock_answered_for_phone.return_value = returned_call_logs

        received_calls = call_history_manager.answered_calls_for_phone(identifier, 2)

        mock_answered_for_phone.assert_called_once_with(identifier, 2)
        self.assertEqual(expected_received_calls, received_calls)

    @patch('xivo_dao.data_handler.call_log.dao.find_all_missed_for_phone')
    def test_missed_calls_for_phone(self, mock_missed_for_phone):
        now = datetime.now()
        identifier = u'sip/abcdef'
        date1 = date2 = date3 = now
        duration1 = 0
        caller_name1 = u'"Foo" <123>'
        duration2 = 0
        caller_name2 = u'"Bar" <456>'
        duration3 = 0
        caller_name3 = u'"Man" <789>'

        call_log_1 = CallLog(date=now,
                             duration=timedelta(0, 0, 0),
                             source_name=u'Foo',
                             source_exten=u'123')

        call_log_2 = CallLog(date=now,
                             duration=timedelta(0, 0, 0),
                             source_name=u'Bar',
                             source_exten=u'456')

        returned_call_logs = [call_log_1, call_log_2]

        expected_received_calls = [ReceivedCall(date1, duration1, caller_name1),
                                   ReceivedCall(date2, duration2, caller_name2)]

        mock_missed_for_phone.return_value = returned_call_logs

        received_calls = call_history_manager.missed_calls_for_phone(identifier, 2)

        mock_missed_for_phone.assert_called_once_with(identifier, 2)
        self.assertEqual(expected_received_calls, received_calls)

    @patch('xivo_dao.data_handler.call_log.dao.find_all_outgoing_for_phone')
    def test_outgoing_calls_for_phone(self, mock_outgoing_for_phone):
        now = datetime.now()
        identifier = u'sip/abcdef'
        date1 = date2 = date3 = now
        duration1 = 1
        caller_name1 = u'123'
        duration2 = 2
        caller_name2 = u'456'
        duration3 = 3
        caller_name3 = u'789'

        call_log_1 = CallLog(date=now,
                             duration=timedelta(0, 1, 0),
                             destination_exten=u'123')

        call_log_2 = CallLog(date=now,
                             duration=timedelta(0, 2, 0),
                             destination_exten=u'456')

        returned_call_logs = [call_log_1, call_log_2]

        expected_sent_calls = [SentCall(date1, duration1, caller_name1),
                               SentCall(date2, duration2, caller_name2)]

        mock_outgoing_for_phone.return_value = returned_call_logs

        sent_calls = call_history_manager.outgoing_calls_for_phone(identifier, 2)

        mock_outgoing_for_phone.assert_called_once_with(identifier, 2)
        self.assertEqual(expected_sent_calls, sent_calls)
