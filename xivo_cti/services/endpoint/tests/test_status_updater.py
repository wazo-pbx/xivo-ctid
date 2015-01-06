# -*- coding: utf-8 -*-

# Copyright (C) 2014 Avencall
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

from ..status_updater import StatusUpdater
from ..status_notifier import StatusNotifier
from hamcrest import assert_that
from hamcrest import equal_to
from mock import Mock
from mock import patch


class TestStatusUpdater(unittest.TestCase):

    def setUp(self):
        self.notifier = Mock(StatusNotifier)
        self.updater = StatusUpdater(self.notifier)

    @patch('xivo_cti.services.endpoint.status_updater.dao')
    def test_update_status_calls_the_dao_to_update(self, dao):
        hint = 'SIP/g19gtv'
        status = 1
        dao.phone.get_phone_id_from_hint.return_value = phone_id = '42'

        self.updater.update_status(hint, status)

        dao.phone.update_status.assert_called_once_with(phone_id, status)

    @patch('xivo_cti.services.endpoint.status_updater.dao')
    def test_that_the_notifier_is_notified_only_when_theres_a_change(self, dao):
        hint = 'SIP/g19gtv'
        status = 1
        dao.phone.get_phone_id_from_hint.return_value = phone_id = '42'
        dao.phone.update_status.return_value = True

        self.updater.update_status(hint, status)

        dao.phone.update_status.assert_called_once_with(phone_id, status)
        self.notifier.notify(phone_id, status)

    @patch('xivo_cti.services.endpoint.status_updater.dao')
    def test_that_the_notifier_is_not_notified_when_theres_no_change(self, dao):
        hint = 'SIP/g19gtv'
        status = 1
        dao.phone.get_phone_id_from_hint.return_value = phone_id = '42'
        dao.phone.update_status.return_value = False

        self.updater.update_status(hint, status)

        dao.phone.update_status.assert_called_once_with(phone_id, status)
        assert_that(self.notifier.notify.call_count, equal_to(0),
                    'The notifier should not be called')
