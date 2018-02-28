# -*- coding: utf-8 -*-
# Copyright (C) 2013-2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

from hamcrest import assert_that, contains, has_entries
from mock import Mock, patch, sentinel
from unittest import TestCase
from xivo_cti.exception import NoSuchUserException, NoSuchLineException

from .. import cti_interface


class TestCallHistoryCTIInterface(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    @patch('xivo_cti.dao.user')
    def test_get_history_unknown_user(self, user_dao):
        user_dao.get_lines.side_effect = NoSuchUserException()

        result = cti_interface.get_history(sentinel.user_id,
                                           sentinel.size)

        assert_that(result, contains('message', {}))

    @patch('xivo_cti.dao.user')
    def test_get_history_when_user_has_no_line(self, user_dao):
        user_dao.get_lines.side_effect = NoSuchLineException()

        result = cti_interface.get_history(sentinel.user_id,
                                           sentinel.size)

        assert_that(result, contains('message', {}))

    @patch('xivo_cti.dao.user')
    @patch('xivo_cti.services.call_history.manager.history_for_phones')
    def test_get_history_empty(self, history, user_dao):
        user_dao.get_lines.return_value = sentinel.phone
        history.return_value = []

        result = cti_interface.get_history(sentinel.user_id,
                                           sentinel.size)

        assert_that(result, contains('message',
                                     has_entries({'class': 'history',
                                                  'history': []})))
        history.assert_called_once_with(sentinel.phone, sentinel.size)

    @patch('xivo_cti.dao.user')
    @patch('xivo_cti.services.call_history.manager.history_for_phones')
    def test_get_history(self, history, user_dao):
        user_dao.get_lines.return_value = sentinel.phone
        history.return_value = [self._call(sentinel.date1,
                                           sentinel.duration1,
                                           sentinel.caller_name1,
                                           sentinel.extension1,
                                           sentinel.mode1),
                                self._call(sentinel.date2,
                                           sentinel.duration2,
                                           sentinel.caller_name2,
                                           sentinel.extension2,
                                           sentinel.mode2)]
        expected_history = [
            {'calldate': sentinel.date1,
             'duration': sentinel.duration1,
             'fullname': sentinel.caller_name1,
             'extension': sentinel.extension1,
             'mode': sentinel.mode1},
            {'calldate': sentinel.date2,
             'duration': sentinel.duration2,
             'fullname': sentinel.caller_name2,
             'extension': sentinel.extension2,
             'mode': sentinel.mode2},
        ]

        result = cti_interface.get_history(sentinel.user_id,
                                           sentinel.size)

        assert_that(result, contains('message', {'class': 'history',
                                                 'history': expected_history}))
        history.assert_called_once_with(sentinel.phone, sentinel.size)

    def _call(self, date, duration, caller_name, extension, mode):
        result = Mock(caller_name=caller_name,
                      duration=duration,
                      extension=extension,
                      mode=mode)
        result.date.isoformat.return_value = date
        return result
