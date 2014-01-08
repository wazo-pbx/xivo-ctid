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
        user_dao.get_line.side_effect = NoSuchUserException()

        result = cti_interface.get_history(sentinel.user_id,
                                           sentinel.mode,
                                           sentinel.size)

        assert_that(result, contains('message', {}))

    @patch('xivo_cti.dao.user')
    def test_get_history_when_user_has_no_line(self, user_dao):
        user_dao.get_line.side_effect = NoSuchLineException()

        result = cti_interface.get_history(sentinel.user_id,
                                           sentinel.mode,
                                           sentinel.size)

        assert_that(result, contains('message', {}))

    @patch('xivo_cti.dao.user')
    @patch('xivo_cti.services.call_history.manager.history_for_phone')
    def test_get_history_empty(self, history, user_dao):
        user_dao.get_line.return_value = sentinel.phone
        history.return_value = []

        result = cti_interface.get_history(sentinel.user_id,
                                           sentinel.mode,
                                           sentinel.size)

        assert_that(result, contains('message',
                                     has_entries({'class': 'history',
                                                  'mode': sentinel.mode,
                                                  'history': []})))
        history.assert_called_once_with(sentinel.phone, sentinel.mode, sentinel.size)

    @patch('xivo_cti.dao.user')
    @patch('xivo_cti.services.call_history.manager.history_for_phone')
    def test_get_history(self, history, user_dao):
        user_dao.get_line.return_value = sentinel.phone
        history.return_value = [self._call(sentinel.date1,
                                           sentinel.duration1,
                                           sentinel.other_end1),
                                self._call(sentinel.date2,
                                           sentinel.duration2,
                                           sentinel.other_end2)]
        expected_history = [
            {'calldate': sentinel.date1,
             'duration': sentinel.duration1,
             'fullname': sentinel.other_end1},
            {'calldate': sentinel.date2,
             'duration': sentinel.duration2,
             'fullname': sentinel.other_end2},
        ]

        result = cti_interface.get_history(sentinel.user_id,
                                           sentinel.mode,
                                           sentinel.size)

        assert_that(result, contains('message', {'class': 'history',
                                                 'mode': sentinel.mode,
                                                 'history': expected_history}))
        history.assert_called_once_with(sentinel.phone, sentinel.mode, sentinel.size)

    def _call(self, date, duration, other_end):
        result = Mock(duration=duration)
        result.date.isoformat.return_value = date
        result.display_other_end.return_value = other_end
        return result
