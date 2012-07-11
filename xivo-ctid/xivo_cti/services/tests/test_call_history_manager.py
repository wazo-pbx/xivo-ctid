# -*- coding: UTF-8 -*-

import unittest
from datetime import datetime
from tests.mock import Mock
from xivo_cti.services.call_history_manager import CallHistoryMgr, ReceivedCall, SentCall


class CallHistoryMgrTest(unittest.TestCase):
    def setUp(self):
        self._cel_dao = Mock()
        self._cel_dao.channels_for_phone.return_value = []
        self._cel_dao.caller_ids = {}
        def caller_id_by_unique_id_side_effect(unique_id):
            return self._cel_dao.caller_ids[unique_id]
        self._cel_dao.caller_id_by_unique_id.side_effect = caller_id_by_unique_id_side_effect

        self._call_history_manager = CallHistoryMgr(self._cel_dao)

    def test_answered_calls_for_phone_with_answered_calls(self):
        phone = {u'protocol': u'sip',
                 u'name': u'abcdef'}
        date1 = datetime.now()
        duration1 = 1
        caller_name1 = u'"Foo" <123>'
        date2 = datetime.now()
        duration2 = 2
        caller_name2 = u'"Bar" <456>'
        date3 = datetime.now()
        duration3 = 3
        caller_name3 = u'"Man" <789>'

        expected_received_calls = [ReceivedCall(date1, duration1, caller_name1),
                                   ReceivedCall(date2, duration2, caller_name2)]

        self._insert_answered_channel_for_phone(linked_id=u'1',
                                                start_time=date1,
                                                duration=duration1,
                                                caller_id=caller_name1)
        self._insert_answered_channel_for_phone(linked_id=u'2',
                                                start_time=date2,
                                                duration=duration2,
                                                caller_id=caller_name2)
        self._insert_answered_channel_for_phone(linked_id=u'3',
                                                start_time=date3,
                                                duration=duration3,
                                                caller_id=caller_name3)

        received_calls = self._call_history_manager.answered_calls_for_phone(phone, 2)

        self._cel_dao.channels_for_phone.called_once_with(phone)
        self._cel_dao.caller_id_by_unique_id.assert_was_called_with(u'1')
        self._cel_dao.caller_id_by_unique_id.assert_was_called_with(u'2')
        self.assertEqual(expected_received_calls, received_calls)

    def test_answered_calls_for_phone_with_no_answered_calls(self):
        phone = {u'protocol': u'sip',
                 u'name': u'abcdef'}
        date = datetime.now()
        duration = 1
        caller_name = u'"Foo" <123>'

        expected_received_calls = []

        self._insert_missed_channel_for_phone(linked_id=u'1',
                                              start_time=date,
                                              caller_id=caller_name)

        received_calls = self._call_history_manager.answered_calls_for_phone(phone, 2)

        self._cel_dao.channels_for_phone.called_once_with(phone)
        self._cel_dao.caller_id_by_unique_id.assert_not_called()
        self.assertEqual(expected_received_calls, received_calls)

    def test_missed_calls_with_missed_calls(self):
        phone = {u'protocol': u'sip',
                 u'name': u'abcdef'}
        date1 = datetime.now()
        caller_name1 = u'"Foo" <123>'
        date2 = datetime.now()
        caller_name2 = u'"Bar" <456>'
        date3 = datetime.now()
        caller_name3 = u'"Man" <789>'

        expected_received_calls = [ReceivedCall(date1, 0.0, caller_name1),
                                   ReceivedCall(date2, 0.0, caller_name2)]

        self._insert_missed_channel_for_phone(linked_id=u'1',
                                              start_time=date1,
                                              caller_id=caller_name1)
        self._insert_missed_channel_for_phone(linked_id=u'2',
                                              start_time=date2,
                                              caller_id=caller_name2)
        self._insert_missed_channel_for_phone(linked_id=u'3',
                                              start_time=date3,
                                              caller_id=caller_name3)

        received_calls = self._call_history_manager.missed_calls_for_phone(phone, 2)

        self._cel_dao.channels_for_phone.called_once_with(phone)
        self._cel_dao.caller_id_by_unique_id.assert_was_called_with(u'1')
        self._cel_dao.caller_id_by_unique_id.assert_was_called_with(u'2')
        self.assertEqual(expected_received_calls, received_calls)

    def test_answered_calls_for_phone_with_no_missed_calls(self):
        phone = {u'protocol': u'sip',
                 u'name': u'abcdef'}
        date = datetime.now()
        duration = 1
        caller_name = u'"Foo" <123>'

        expected_received_calls = []

        self._insert_answered_channel_for_phone(linked_id=u'1',
                                                start_time=date,
                                                duration=duration,
                                                caller_id=caller_name)

        received_calls = self._call_history_manager.missed_calls_for_phone(phone, 2)

        self._cel_dao.channels_for_phone.called_once_with(phone)
        self._cel_dao.caller_id_by_unique_id.assert_not_called()
        self.assertEqual(expected_received_calls, received_calls)

    def test_outgoing_calls_with_outgoing_calls(self):
        phone = {u'protocol': u'sip',
                 u'name': u'abcdef'}
        date1 = datetime.now()
        called_exten1 = u'123'
        duration1 = 1
        date2 = datetime.now()
        called_exten2 = u'456'
        duration2 = 2
        date3 = datetime.now()
        called_exten3 = u'789'
        duration3 = 3

        expected_received_calls = [SentCall(date1, duration1, called_exten1),
                                   SentCall(date2, duration2, called_exten2)]

        self._insert_outgoing_channel_for_phone(start_time=date1,
                                                duration=duration1,
                                                called_exten=called_exten1)
        self._insert_outgoing_channel_for_phone(start_time=date2,
                                                duration=duration2,
                                                called_exten=called_exten2)
        self._insert_outgoing_channel_for_phone(start_time=date3,
                                                duration=duration3,
                                                called_exten=called_exten3)

        received_calls = self._call_history_manager.outgoing_calls_for_phone(phone, 2)

        self._cel_dao.channels_for_phone.called_once_with(phone)
        self.assertEqual(expected_received_calls, received_calls)

    def test_outgoing_calls_for_phone_with_no_outgoing_calls(self):
        phone = {u'protocol': u'sip',
                 u'name': u'abcdef'}
        date = datetime.now()
        duration = 1
        called_exten = u'123'

        expected_sent_calls = []

        self._insert_outgoing_channel_for_phone(start_time=date,
                                                duration=duration,
                                                called_exten=called_exten)

        sent_calls = self._call_history_manager.missed_calls_for_phone(phone, 2)

        self._cel_dao.channels_for_phone.called_once_with(phone)
        self.assertEqual(expected_sent_calls, sent_calls)

    def _insert_answered_channel_for_phone(self,
                                           linked_id,
                                           start_time,
                                           duration,
                                           caller_id):
        channel = self._create_channel(linked_id, start_time)
        channel.answer_duration.return_value = duration
        channel.is_caller.return_value = False
        channel.is_answered.return_value = True
        self._insert_channel(channel)
        self._insert_caller_id(linked_id, caller_id)

    def _insert_missed_channel_for_phone(self,
                                         linked_id,
                                         start_time,
                                         caller_id):
        channel = self._create_channel(linked_id, start_time)
        channel.answer_duration.return_value = 0.0
        channel.is_caller.return_value = False
        channel.is_answered.return_value = False
        self._insert_channel(channel)
        self._insert_caller_id(linked_id, caller_id)

    def _insert_outgoing_channel_for_phone(self,
                                           start_time,
                                           duration,
                                           called_exten):
        channel = self._create_channel(u'0', start_time)
        channel.answer_duration.return_value = duration
        channel.exten.return_value = called_exten
        channel.is_caller.return_value = True
        self._insert_channel(channel)

    def _create_channel(self,
                        linked_id,
                        start_time):
        channel = Mock()
        channel.linked_id.return_value = linked_id
        channel.channel_start_time.return_value = start_time
        return channel

    def _insert_channel(self, channel):
        self._cel_dao.channels_for_phone.return_value.append(channel)

    def _insert_caller_id(self, linked_id, caller_id):
        self._cel_dao.caller_ids[linked_id] = caller_id

    def _test_outgoing_calls_for_endpoint(self):
        date = datetime.now()
        duration = 1
        extension = u'100'

        cel_channel = Mock()
        cel_channel.channel_start_time.return_value = date
        cel_channel.answer_duration.return_value = duration
        cel_channel.exten.return_value = extension

        cel_dao = Mock()
        cel_dao.outgoing_channels_for_endpoint.return_value = [
            cel_channel
        ]

        call_history_mgr = CallHistoryMgr(cel_dao)
        sent_calls = call_history_mgr.outgoing_calls_for_endpoint(u'SIP/A', 5)

        self.assertEqual([SentCall(date, duration, extension)], sent_calls)
