# -*- coding: utf-8 -*-

# Copyright (C) 2016 Avencall
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

from hamcrest import assert_that, calling, equal_to, not_, raises
from mock import Mock, sentinel as s

from xivo_cti.bus_listener import BusListener
from xivo_cti.innerdata import Safe
from xivo_cti.task_queue import _TaskQueue as TaskQueue

from ..cache_updater import CacheUpdater

SOME_USER_ID = 10
SOME_LINE_ID = 12
SOME_XIVO_UUID = 'ae90aff8-8947-4111-9d25-50e0f1328ea8'
SOME_OTHER_XIVO_UUID = '14af24ad-b6d0-4297-8b64-fe551dc49cf1'


class TestCacheUpdater(unittest.TestCase):

    def setUp(self):
        self.listener = Mock(BusListener)
        self.task_queue = Mock(TaskQueue)
        self.xivo_uuid = SOME_XIVO_UUID
        self.innerdata = Mock(Safe)

        self.updater = CacheUpdater(self.task_queue, self.xivo_uuid, self.innerdata)
        self.updater.subscribe_to_bus(self.listener)

    def test_that_on_user_line_associated_the_user_is_updated(self):
        self.updater._on_user_line_associated(s.user_id, s.line_id)

        self.innerdata.update_config_list('users', 'edit', s.user_id)

    def test_that_on_user_line_associated_the_phone_is_added(self):
        self.updater._on_user_line_associated(s.user_id, s.line_id)

        self.innerdata.update_config_list('phones', 'add', s.line_id)

    def test_that_user_associated_messages_triggers_a_call_to_on_user_line_associated(self):
        event = self._new_user_line_associated_event(SOME_USER_ID, SOME_LINE_ID)

        self.updater.on_bus_user_line_associated(event, Mock())

        self.task_queue.put.assert_called_once_with(self.updater._on_user_line_associated,
                                                    str(SOME_USER_ID), str(SOME_LINE_ID))

    def test_that_user_associated_messages_does_nothing_on_malformed_events(self):
        assert_that(calling(self.updater.on_bus_user_line_associated)
                    .with_args({}, Mock()),
                    not_(raises(Exception)))

        assert_that(calling(self.updater.on_bus_user_line_associated)
                    .with_args('{"name": "line_associated"}', Mock()),
                    not_(raises(Exception)))

    def test_that_user_associated_messages_from_another_xivo_does_nothing(self):
        event = self._new_user_line_associated_event(SOME_USER_ID, SOME_LINE_ID, SOME_OTHER_XIVO_UUID)

        self.updater.on_bus_user_line_associated(event, Mock())

        assert_that(self.task_queue.put.called, equal_to(False))

    def _new_user_line_associated_event(self, user_id, line_id, xivo_uuid=None):
        return {u'data': {u'line_id': line_id,
                          u'main_user': True,
                          u'user_id': user_id,
                          u'main_line': True},
                u'name': u'line_associated',
                u'origin_uuid': xivo_uuid or self.xivo_uuid}
