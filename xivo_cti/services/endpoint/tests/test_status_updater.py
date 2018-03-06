# -*- coding: utf-8 -*-
# Copyright 2014-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import unittest

from hamcrest import assert_that
from hamcrest import equal_to
from mock import Mock
from mock import patch

from ..status_updater import StatusUpdater
from ..status_notifier import StatusNotifier


class TestStatusUpdater(unittest.TestCase):

    def setUp(self):
        self.notifier = Mock(StatusNotifier)
        self.updater = StatusUpdater(self.notifier)

    @patch('xivo_cti.services.endpoint.status_updater.dao')
    def test_update_status_calls_the_dao_to_update(self, dao):
        hint = 'SIP/g19gtv'
        status = 1
        phone_id = '42'
        dao.phone.get_phone_ids_from_hint.return_value = [phone_id]

        self.updater.update_status(hint, status)

        dao.phone.update_status.assert_called_once_with(phone_id, status)

    @patch('xivo_cti.services.endpoint.status_updater.dao')
    def test_that_the_notifier_is_notified_only_when_theres_a_change(self, dao):
        hint = 'SIP/g19gtv'
        status = 1
        phone_id = '42'
        dao.phone.get_phone_ids_from_hint.return_value = [phone_id]
        dao.phone.update_status.return_value = True

        self.updater.update_status(hint, status)

        dao.phone.update_status.assert_called_once_with(phone_id, status)
        self.notifier.notify(phone_id, status)

    @patch('xivo_cti.services.endpoint.status_updater.dao')
    def test_that_the_notifier_is_not_notified_when_theres_no_change(self, dao):
        hint = 'SIP/g19gtv'
        status = 1
        phone_id = '42'
        dao.phone.get_phone_ids_from_hint.return_value = [phone_id]
        dao.phone.update_status.return_value = False

        self.updater.update_status(hint, status)

        dao.phone.update_status.assert_called_once_with(phone_id, status)
        assert_that(self.notifier.notify.call_count, equal_to(0),
                    'The notifier should not be called')
