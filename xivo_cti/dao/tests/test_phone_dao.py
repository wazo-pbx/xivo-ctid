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

from hamcrest import assert_that
from hamcrest import contains
from hamcrest import equal_to
from mock import Mock
from mock import sentinel
from xivo_cti.innerdata import Safe
from xivo_cti.lists.phones_list import PhonesList

from ..phone_dao import PhoneDAO
from ..phone_dao import NoSuchPhoneException


class TestPhoneDAO(unittest.TestCase):

    def setUp(self):
        self._innerdata = Mock(Safe)
        self._innerdata.xod_config = {'phones': {}}
        self._innerdata.xod_status = {'phones': {}}
        self.dao = PhoneDAO(self._innerdata)

    def test_get_status(self):
        phone_id = '42'

        self._innerdata.xod_status['phones'][phone_id] = {'hintstatus': sentinel.status}

        assert_that(self.dao.get_status(phone_id), equal_to(sentinel.status))

    def test_get_status_no_list(self):
        phone_id = '42'

        self.assertRaises(NoSuchPhoneException, self.dao.get_status, phone_id)

    def test_update_status(self):
        phone_id = '42'

        self._innerdata.xod_status['phones'][phone_id] = {'hintstatus': sentinel.status}

        self.dao.update_status(phone_id, sentinel.new_status)

        assert_that(self._innerdata.xod_status['phones'][phone_id]['hintstatus'],
                    equal_to(sentinel.new_status))

    def test_that_update_status_return_true_or_false_to_indicate_a_change_in_status(self):
        phone_id = '42'

        self._innerdata.xod_status['phones'][phone_id] = {'hintstatus': sentinel.status}

        res = self.dao.update_status(phone_id, sentinel.new_status)

        assert_that(res, equal_to(True))

        res = self.dao.update_status(phone_id, sentinel.new_status)

        assert_that(res, equal_to(False))

    def test_get_phone_ids_from_hint(self):
        phones = self._innerdata.xod_config['phones'] = Mock(PhonesList)
        phones.get_phone_id_from_proto_and_name.return_value = sentinel.phone_id

        hint = 'SIP/abcdef'

        phone_ids = self.dao.get_phone_ids_from_hint(hint)

        assert_that(phone_ids, contains(sentinel.phone_id))
        phones.get_phone_id_from_proto_and_name.assert_called_once_with('sip', 'abcdef')

    def test_get_phone_ids_from_hint_no_phone(self):
        phones = self._innerdata.xod_config['phones'] = Mock(PhonesList)
        phones.get_phone_id_from_proto_and_name.return_value = None

        phone_ids = self.dao.get_phone_ids_from_hint('SCCP/notfound')

        assert_that(phone_ids, contains())

    def test_get_phone_ids_from_hint_with_a_none_phone_hint(self):
        phone_ids = self.dao.get_phone_ids_from_hint('meetme:4001')

        assert_that(phone_ids, contains())
