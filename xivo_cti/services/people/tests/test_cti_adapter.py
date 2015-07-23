# -*- coding: utf-8 -*-

# Copyright (C) 2014-2015 Avencall
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


from concurrent import futures
from mock import Mock, patch, sentinel as s
from unittest import TestCase

from xivo_cti import dao
from xivo_cti.async_runner import AsyncRunner, synchronize
from xivo_cti.task_queue import new_task_queue

from ..cti_adapter import PeopleCTIAdapter


class TestCTIAdapter(TestCase):

    def setUp(self):
        self.task_queue = new_task_queue()
        self.async_runner = AsyncRunner(futures.ThreadPoolExecutor(max_workers=1), self.task_queue)
        self.cti_connection = Mock(connection_details={'auth_token': s.token})
        self.cti_server = Mock()
        with patch('xivo_cti.services.people.cti_adapter.config', {'dird': {}}):
            with patch('xivo_cti.services.people.cti_adapter.Client') as Client:
                self.cti_adapter = PeopleCTIAdapter(self.async_runner, self.cti_server)
                self.client = Client.return_value

    def tearDown(self):
        self.task_queue.close()

    @patch('xivo_cti.dao.user', Mock())
    def test_get_headers(self):
        dao.user.get_context = Mock(return_value=s.profile)

        with synchronize(self.async_runner):
            self.cti_adapter.get_headers(self.cti_connection, s.user_id)

        self.client.directories.headers.assert_called_once_with(profile=s.profile, token=s.token)

    def test_send_headers_result(self):
        user_id = 12
        headers = {
            'column_headers': Mock(),
            'column_types': Mock(),
        }

        self.cti_adapter._send_headers_result(user_id, headers)

        self.cti_server.send_to_cti_client.assert_called_once_with(
            'xivo/12',
            {
                'class': 'people_headers_result',
                'column_headers': headers['column_headers'],
                'column_types': headers['column_types']
            }
        )

    @patch('xivo_cti.dao.user', Mock())
    def test_lookup(self):
        dao.user.get_context = Mock(return_value=s.profile)

        with synchronize(self.async_runner):
            self.cti_adapter.search(self.cti_connection, s.user_id, s.term)

        self.client.directories.lookup.assert_called_once_with(profile=s.profile, term=s.term, token=s.token)

    def test_send_lookup_result(self):
        user_id = 12
        results = {
            'term': s.term,
            'column_headers': s.column_headers,
            'column_types': s.column_types,
            'results': s.results,
        }

        self.cti_adapter._send_lookup_result(user_id, results)

        self.cti_server.send_to_cti_client.assert_called_once_with(
            'xivo/12',
            {
                'class': 'people_search_result',
                'term': s.term,
                'column_headers': s.column_headers,
                'column_types': s.column_types,
                'results': s.results,
            }
        )

    @patch('xivo_cti.dao.user', Mock())
    def test_favorites(self):
        dao.user.get_context = Mock(return_value=s.profile)

        with synchronize(self.async_runner):
            self.cti_adapter.favorites(self.cti_connection, s.user_id)

        self.client.directories.favorites.assert_called_once_with(profile=s.profile, token=s.token)

    def test_send_favorites_result(self):
        user_id = 12
        results = {
            'column_headers': s.column_headers,
            'column_types': s.column_types,
            'results': s.results,
        }

        self.cti_adapter._send_favorites_result(user_id, results)

        self.cti_server.send_to_cti_client.assert_called_once_with(
            'xivo/12',
            {
                'class': 'people_favorites_result',
                'column_headers': s.column_headers,
                'column_types': s.column_types,
                'results': s.results,
            }
        )

    @patch('xivo_cti.dao.user', Mock())
    def test_set_favorite_with_new_favorite(self):
        source = "internal"
        source_entry_id = "123456789"
        enabled = True
        dao.user.get_context = Mock(return_value=s.profile)

        with synchronize(self.async_runner):
            self.cti_adapter.set_favorite(self.cti_connection, s.user_id, source, source_entry_id, enabled)

        self.client.directories.new_favorite.assert_called_once_with(directory=source,
                                                                     contact=source_entry_id,
                                                                     token=s.token)

    @patch('xivo_cti.dao.user', Mock())
    def test_set_favorite_with_remove_favorite(self):
        source = "internal"
        source_entry_id = "123456789"
        enabled = False
        dao.user.get_context = Mock(return_value=s.profile)

        with synchronize(self.async_runner):
            self.cti_adapter.set_favorite(self.cti_connection, s.user_id, source, source_entry_id, enabled)

        self.client.directories.remove_favorite.assert_called_once_with(directory=source,
                                                                        contact=source_entry_id,
                                                                        token=s.token)

    def test_send_favorite_update(self):
        user_id = 12
        source = "internal"
        source_entry_id = "123456789"
        enabled = True
        result = None

        self.cti_adapter._send_favorite_update(user_id, source, source_entry_id, enabled, result)

        self.cti_server.send_to_cti_client.assert_called_once_with(
            'xivo/12',
            {
                'class': 'people_favorite_update',
                'data': {
                    'source': source,
                    'source_entry_id': source_entry_id,
                    'favorite': enabled,
                }
            }
        )

    @patch('xivo_cti.dao.user', Mock())
    def test_personal_contacts(self):
        dao.user.get_context = Mock(return_value=s.profile)

        with synchronize(self.async_runner):
            self.cti_adapter.personal_contacts(self.cti_connection, s.user_id)

        self.client.directories.personal.assert_called_once_with(profile=s.profile, token=s.token)

    def test_send_personal_contacts_result(self):
        user_id = 12
        results = {
            'column_headers': s.column_headers,
            'column_types': s.column_types,
            'results': s.results,
        }

        self.cti_adapter._send_personal_contacts_result(user_id, results)

        self.cti_server.send_to_cti_client.assert_called_once_with(
            'xivo/12',
            {
                'class': 'people_personal_contacts_result',
                'column_headers': s.column_headers,
                'column_types': s.column_types,
                'results': s.results,
            }
        )

    @patch('xivo_cti.dao.user', Mock())
    def test_create_personal_contact(self):
        contact_infos = {'firstname': 'Bob',
                         'lastname': 'Le Bricoleur',
                         'random_key': 'random_value'}
        dao.user.get_context = Mock(return_value=s.profile)

        with synchronize(self.async_runner):
            self.cti_adapter.create_personal_contact(self.cti_connection, s.user_id, contact_infos)

        self.client.personal.create.assert_called_once_with(contact_infos=contact_infos, token=s.token)

    def test_send_personal_contact_created(self):
        user_id = 12
        result = None

        self.cti_adapter._send_personal_contact_created(user_id, result)

        self.cti_server.send_to_cti_client.assert_called_once_with(
            'xivo/12',
            {
                'class': 'people_personal_contact_created'
            }
        )

    @patch('xivo_cti.dao.user', Mock())
    def test_delete_personal_contact(self):
        source = "internal"
        source_entry_id = "123456789"
        dao.user.get_context = Mock(return_value=s.profile)

        with synchronize(self.async_runner):
            self.cti_adapter.delete_personal_contact(self.cti_connection, s.user_id, source, source_entry_id)

        self.client.personal.delete.assert_called_once_with(contact_id=source_entry_id, token=s.token)

    def test_send_personal_contact_deleted(self):
        user_id = 12
        source = "internal"
        source_entry_id = "123456789"
        result = None

        self.cti_adapter._send_personal_contact_deleted(user_id, source, source_entry_id, result)

        self.cti_server.send_to_cti_client.assert_called_once_with(
            'xivo/12',
            {
                'class': 'people_personal_contact_deleted',
                'data': {
                    'source': source,
                    'source_entry_id': source_entry_id,
                }
            }
        )
