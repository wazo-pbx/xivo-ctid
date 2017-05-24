# -*- coding: utf-8 -*-

# Copyright 2013-2017 The Wazo Authors  (see the AUTHORS file)
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

from hamcrest import assert_that, same_instance, equal_to
from mock import sentinel, patch
from datetime import datetime, timedelta
from xivo_cti.services.call_history.manager import Call, HistoryMode
from xivo_cti.services.call_history import manager as call_history_manager
from xivo_dao.alchemy.call_log import CallLog


class CallHistoryMgrTest(unittest.TestCase):

    @patch('xivo_cti.services.call_history.manager.all_calls_for_phones')
    def test_history_for_phones_all(self, all_calls):
        identifiers = [u'sip/abcdef', u'sip/ghijk']
        phones = [{u'protocol': u'sip', u'name': u'abcdef'},
                  {u'protocol': u'sip', u'name': u'ghijk'}]
        all_calls.return_value = sentinel.calls

        result = call_history_manager.history_for_phones(phones,
                                                         sentinel.limit)

        all_calls.assert_called_once_with(identifiers, sentinel.limit)
        assert_that(result, same_instance(sentinel.calls))

    @patch('xivo_dao.resources.call_log.dao.find_all_history_for_phones')
    def test_all_calls_for_phones(self, mock_all_for_phones):
        now = datetime.now()
        identifiers = [u'sip/abcdef', u'sip/ghijk']
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
                             destination_line_identity=identifiers[0],
                             duration=timedelta(0, 2, 0),
                             source_name=u'Foo',
                             source_exten=u'123')

        call_log_2 = CallLog(answered=False,
                             date=now,
                             destination_line_identity=identifiers[1],
                             duration=timedelta(0, 0, 0),
                             source_name=u'Bar',
                             source_exten=u'456')

        call_log_3 = CallLog(date=now,
                             destination_line_identity=None,
                             duration=timedelta(0, 3, 0),
                             destination_exten=u'789')

        returned_call_logs = [call_log_1, call_log_2, call_log_3]

        expected_all_calls = [Call(date1, duration1, caller_name1, extension1, mode1),
                              Call(date2, duration2, caller_name2, extension2, mode2),
                              Call(date3, duration3, caller_name3, extension3, mode3)]

        mock_all_for_phones.return_value = returned_call_logs

        all_calls = call_history_manager.all_calls_for_phones(identifiers, 3)

        mock_all_for_phones.assert_called_once_with(identifiers, 3)
        assert_that(all_calls, equal_to(expected_all_calls))
