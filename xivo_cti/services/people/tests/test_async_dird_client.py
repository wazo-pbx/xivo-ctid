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

from ..async_dird_client import AsyncDirdClient

from hamcrest import assert_that
from hamcrest import equal_to
from mock import patch
from mock import Mock
from mock import sentinel
from unittest import TestCase


@patch('xivo_cti.services.people.async_dird_client.Client')
class TestDird(TestCase):

    def setUp(self):
        self.task_queue = Mock()

    def test_client(self, MockedClient):
        async_dird_client = AsyncDirdClient(self.task_queue)
        assert_that(async_dird_client._client, equal_to(MockedClient.return_value))
        MockedClient.assert_called_once_with(host='localhost', port=9489, version='0.1')

    def test_headers(self, MockedClient):
        MockedClient.return_value.directories.headers.return_value = 'my-headers'

        async_dird_client = AsyncDirdClient(self.task_queue)

        async_dird_client.headers('my-profile', sentinel.cb)

        async_dird_client.executor.shutdown(wait=True)

        self.task_queue.put.assert_called_once_with(sentinel.cb, 'my-headers')
        MockedClient.return_value.directories.headers.assert_called_once_with(profile='my-profile')

    def test_lookup(self, MockedClient):
        MockedClient.return_value.directories.lookup.return_value = 'my-results'

        async_dird_client = AsyncDirdClient(self.task_queue)

        async_dird_client.lookup('my-profile', 'alice', sentinel.cb)

        async_dird_client.executor.shutdown(wait=True)

        self.task_queue.put.assert_called_once_with(sentinel.cb, 'my-results')
        MockedClient.return_value.directories.lookup.assert_called_once_with(
            profile='my-profile', term='alice')
