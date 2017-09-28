# -*- coding: utf-8 -*-

# Copyright 2014-2017 The Wazo Authors  (see the AUTHORS file)
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

from ..status_notifier import StatusNotifier
from ..status_notifier import EndpointStatusUpdateEvent
from xivo_cti.ctiserver import CTIServer
from mock import Mock


class TestStatusNotifier(unittest.TestCase):

    def setUp(self):
        self._ctiserver = Mock(CTIServer)
        self._bus_publisher = Mock()
        self._innerdata = Mock()
        self._notifier = StatusNotifier(self._ctiserver,
                                        self._bus_publisher,
                                        self._innerdata)

    def test_that_notify_calls_send_cti_event(self):
        phone_id, status = '42', 8
        user_id = '12'
        user_uuid = '12-34'
        self._innerdata.xod_config = {
            'phones': Mock(keeplist={phone_id: {'iduserfeatures': user_id}}),
            'users': Mock(keeplist={user_id: {'uuid': user_uuid}}),
        }

        self._notifier.notify(phone_id, status)

        self._ctiserver.send_cti_event.assert_called_once_with({
            'class': 'getlist',
            'listname': 'phones',
            'function': 'updatestatus',
            'tipbxid': 'xivo',
            'tid': phone_id,
            'status': {'hintstatus': status},
        })

    def test_that_notify_sends_endpoint_status_update_event_on_the_bus(self):
        phone_id = '42'
        user_id = '12'
        user_uuid = '12-34'
        new_status = 0
        self._innerdata.xod_config = {
            'phones': Mock(keeplist={phone_id: {'iduserfeatures': user_id}}),
            'users': Mock(keeplist={user_id: {'uuid': user_uuid}}),
        }

        self._notifier.notify(phone_id, new_status)

        expected_event = EndpointStatusUpdateEvent(phone_id, new_status)

        self._bus_publisher.publish.assert_called_once_with(expected_event, headers={'user_uuid:12-34': True})
