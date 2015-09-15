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

from ..cti_adapter import OldProtocolCTIAdapter, PeopleCTIAdapter
from ..old_directory_formatter import OldDirectoryFormatter


class TestOldProtocolCTIAdapter(TestCase):

    profile = '__switchboard_directory'

    def setUp(self):
        self.task_queue = new_task_queue()
        self.async_runner = AsyncRunner(futures.ThreadPoolExecutor(max_workers=1), self.task_queue)
        self.cti_server = Mock()
        with patch('xivo_cti.services.people.cti_adapter.config', {'dird': {}}):
            with patch('xivo_cti.services.people.cti_adapter.Client') as Client:
                self.cti_adapter = OldProtocolCTIAdapter(self.async_runner, self.cti_server)
                self.client = Client.return_value
        self.formatter = self.cti_adapter._old_formatter = Mock(OldDirectoryFormatter)

    def test_get_headers(self):
        with synchronize(self.async_runner):
            self.cti_adapter.get_headers(s.token, s.user_id)

        self.client.directories.headers.assert_called_once_with(profile=self.profile, token=s.token)

    def test_send_headers_result(self):
        user_id = 12
        headers = {
            'column_headers': Mock(),
            'column_types': Mock(),
        }

        self.cti_adapter._send_headers_result(user_id, headers)

        self.cti_server.send_to_cti_client.assert_called_once_with(
            'xivo/12', {'class': 'directory_headers',
                        'headers': self.formatter.format_headers.return_value})
        self.formatter.format_headers.assert_called_once_with(headers)

    def test_lookup(self):
        with synchronize(self.async_runner):
            self.cti_adapter.lookup(s.token, s.user_id, s.term)

        self.client.directories.lookup.assert_called_once_with(profile=self.profile,
                                                               term=s.term, token=s.token)

    @patch('xivo_cti.services.people.cti_adapter.DirectoryResultFormatter')
    def test_send_lookup_result(self, MockedDirectoryResultFormatter):
        self.formatter.format_results.return_value = Mock(), Mock(), Mock()
        user_id = 12
        results = {
            'term': s.term,
            'column_headers': s.column_headers,
            'column_types': s.column_types,
            'results': s.results,
        }

        self.cti_adapter._send_lookup_result(user_id, results)

        self.cti_server.send_to_cti_client.assert_called_once_with(
            'xivo/12', {'class': 'directory_search_result',
                        'pattern': s.term,
                        'results': MockedDirectoryResultFormatter.format.return_value})

    @patch('xivo_cti.dao.user')
    def test_directory_search(self, mocked_user_dao):
        with synchronize(self.async_runner):
            self.cti_adapter.directory_search(s.token, s.user_id, s.term, s.commandid)

        self.client.directories.lookup.assert_called_once_with(
            profile=mocked_user_dao.get_context.return_value, term=s.term, token=s.token)

    def test_send_directory_search_result(self):
        user_id = 12
        results = {
            'term': s.term,
            'column_headers': s.column_headers,
            'column_types': s.column_types,
            'results': s.results,
        }
        self.formatter.format_results.return_value = s.headers, s.types, s.resultlist

        self.cti_adapter._send_directory_search_result(user_id, s.commandid, results)

        expected_message = {'class': 'directory',
                            'headers': s.headers,
                            'replyid': s.commandid,
                            'resultlist': s.resultlist,
                            'status': 'ok'}
        self.cti_server.send_to_cti_client.assert_called_once_with(
            'xivo/12', expected_message)
        self.formatter.format_results.assert_called_once_with(results)


class TestCTIAdapter(TestCase):

    def setUp(self):
        self.task_queue = new_task_queue()
        self.async_runner = AsyncRunner(futures.ThreadPoolExecutor(max_workers=1), self.task_queue)
        self.cti_server = Mock()
        with patch('xivo_cti.services.people.cti_adapter.config', {'dird': {}}):
            with patch('xivo_cti.services.people.cti_adapter.Client') as Client:
                self.cti_adapter = PeopleCTIAdapter(self.async_runner, self.cti_server)
                self.client = Client.return_value

    def tearDown(self):
        self.task_queue.close()

    @patch('xivo_cti.services.people.cti_adapter.config', {'uuid': s.xivo_uuid})
    @patch('xivo_cti.services.people.cti_adapter.dao', Mock(user=Mock(get_agent_id=Mock(return_value='26'),
                                                                      get_line=Mock(return_value={'id': '24'}))))
    def test_get_relations(self):
        user_id = '42'

        self.cti_adapter.get_relations(user_id)

        expected_msg = {'class': 'relations',
                        'data': {'xivo_uuid': s.xivo_uuid,
                                 'user_id': 42,
                                 'endpoint_id': 24,
                                 'agent_id': 26}}
        self.cti_server.send_to_cti_client.assert_called_once_with('xivo/42', expected_msg)

    @patch('xivo_cti.dao.user', Mock())
    def test_get_headers(self):
        dao.user.get_context = Mock(return_value=s.profile)

        with synchronize(self.async_runner):
            self.cti_adapter.get_headers(s.token, s.user_id)

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
            self.cti_adapter.search(s.token, s.user_id, s.term)

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
            self.cti_adapter.favorites(s.token, s.user_id)

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
        source = 'internal'
        source_entry_id = '123456789'
        enabled = True
        dao.user.get_context = Mock(return_value=s.profile)

        with synchronize(self.async_runner):
            self.cti_adapter.set_favorite(s.token, s.user_id, source, source_entry_id, enabled)

        self.client.directories.new_favorite.assert_called_once_with(directory=source,
                                                                     contact=source_entry_id,
                                                                     token=s.token)

    @patch('xivo_cti.dao.user', Mock())
    def test_set_favorite_with_remove_favorite(self):
        source = 'internal'
        source_entry_id = '123456789'
        enabled = False
        dao.user.get_context = Mock(return_value=s.profile)

        with synchronize(self.async_runner):
            self.cti_adapter.set_favorite(s.token, s.user_id, source, source_entry_id, enabled)

        self.client.directories.remove_favorite.assert_called_once_with(directory=source,
                                                                        contact=source_entry_id,
                                                                        token=s.token)

    def test_send_favorite_update(self):
        user_id = 12
        source = 'internal'
        source_entry_id = '123456789'
        enabled = True
        result = None

        self.cti_adapter._send_favorite_update(user_id, source, source_entry_id, enabled, result)

        self.cti_server.send_to_cti_client.assert_called_once_with(
            'xivo/12',
            {
                'class': 'people_favorite_update',
                'source': source,
                'source_entry_id': source_entry_id,
                'favorite': enabled,
            }
        )

    @patch('xivo_cti.dao.user', Mock())
    def test_personal_contacts(self):
        dao.user.get_context = Mock(return_value=s.profile)

        with synchronize(self.async_runner):
            self.cti_adapter.personal_contacts(s.token, s.user_id)

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

    def test_purge_personal_contacts(self):
        with synchronize(self.async_runner):
            self.cti_adapter.purge_personal_contacts(s.token, s.user_id)

        self.client.personal.purge.assert_called_once_with(token=s.token)

    def test_send_personal_contacts_purged(self):
        user_id = 12
        result = None
        self.cti_adapter._send_personal_contacts_purged(user_id, result)

        self.cti_server.send_to_cti_client.assert_called_once_with(
            'xivo/12',
            {
                'class': 'people_personal_contacts_purged'
            }
        )

    def test_create_personal_contact(self):
        contact_infos = {'firstname': 'Bob',
                         'lastname': 'Le Bricoleur',
                         'random_key': 'random_value'}

        with synchronize(self.async_runner):
            self.cti_adapter.create_personal_contact(s.token, s.user_id, contact_infos)

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

    def test_delete_personal_contact(self):
        source = 'internal'
        source_entry_id = '123456789'

        with synchronize(self.async_runner):
            self.cti_adapter.delete_personal_contact(s.token, s.user_id, source, source_entry_id)

        self.client.personal.delete.assert_called_once_with(contact_id=source_entry_id, token=s.token)

    def test_send_personal_contact_deleted(self):
        user_id = 12
        source = 'internal'
        source_entry_id = '123456789'
        result = None

        self.cti_adapter._send_personal_contact_deleted(user_id, source, source_entry_id, result)

        self.cti_server.send_to_cti_client.assert_called_once_with(
            'xivo/12',
            {
                'class': 'people_personal_contact_deleted',
                'source': source,
                'source_entry_id': source_entry_id,
            }
        )

    def test_edit_personal_contact(self):
        source = 'personal'
        source_entry_id = '123456789'
        contact_infos = {'firstname': 'Bob',
                         'lastname': 'Le Bricoleur',
                         'random_key': 'random_value'}

        with synchronize(self.async_runner):
            self.cti_adapter.edit_personal_contact(s.token,
                                                   s.user_id,
                                                   source,
                                                   source_entry_id,
                                                   contact_infos)

        self.client.personal.edit.assert_called_once_with(contact_id=source_entry_id,
                                                          contact_infos=contact_infos,
                                                          token=s.token)

    def test_send_personal_contact_raw_update(self):
        user_id = 12
        source = 'personal'
        source_entry_id = '123456789'
        result = None

        self.cti_adapter._send_personal_contact_raw_update(user_id, source, source_entry_id, result)

        self.cti_server.send_to_cti_client.assert_called_once_with(
            'xivo/12',
            {
                'class': 'people_personal_contact_raw_update',
                'source': source,
                'source_entry_id': source_entry_id,
            }
        )

    def test_personal_contact_raw(self):
        source = 'personal'
        source_entry_id = '123456789'

        with synchronize(self.async_runner):
            self.cti_adapter.personal_contact_raw(s.token, s.user_id, source, source_entry_id)

        self.client.personal.get.assert_called_once_with(contact_id=source_entry_id, token=s.token)

    def test_send_personal_contact_raw_result(self):
        user_id = 12
        source = 'personal'
        source_entry_id = '123456789'
        result = {'firstname': 'Bob',
                  'lastname': 'Le Bricoleur',
                  'random_key': 'random_value'}

        self.cti_adapter._send_personal_contact_raw_result(user_id, source, source_entry_id, result)

        self.cti_server.send_to_cti_client.assert_called_once_with(
            'xivo/12',
            {
                'class': 'people_personal_contact_raw_result',
                'source': source,
                'source_entry_id': source_entry_id,
                'contact_infos': {
                    'firstname': 'Bob',
                    'lastname': 'Le Bricoleur',
                    'random_key': 'random_value'
                }
            }
        )

    def test_export_personal_contacts_csv(self):
        with synchronize(self.async_runner):
            self.cti_adapter.export_personal_contacts_csv(s.token, s.user_id)

        self.client.personal.export_csv.assert_called_once_with(token=s.token)

    def test_send_export_personal_contact_csv_result(self):
        user_id = 12
        result = 'firstname,lastname\r\nBob,the Buidler\r\n,Alice,Wonderland'

        self.cti_adapter._send_export_personal_contacts_csv_result(user_id, result)

        self.cti_server.send_to_cti_client.assert_called_once_with(
            'xivo/12',
            {
                'class': 'people_export_personal_contacts_csv_result',
                'csv_contacts': result
            }
        )

    def test_import_personal_contacts_csv(self):
        csv_contacts = 'firstname,lastname\r\nBob, the Builder\r\nAlice, Wonderland\r\n'
        with synchronize(self.async_runner):
            self.cti_adapter.import_personal_contacts_csv(s.token, s.user_id, csv_contacts)

        self.client.personal.import_csv.assert_called_once_with(csv_text=csv_contacts, token=s.token)

    def test_send_import_personal_contact_csv_result(self):
        user_id = 12
        result = {
            'failed': [
                {
                    'line': 3,
                    'errors': ['missing fields']
                }
            ],
            'created': [
                {
                    'firstname': 'Toto',
                    'lastname': 'Bélanger'
                },
                {
                    'firstname': 'Tata',
                    'lastanem': 'Bergeron'
                }
            ]
        }

        self.cti_adapter._send_import_personal_contacts_csv_result(user_id, result)

        self.cti_server.send_to_cti_client.assert_called_once_with(
            'xivo/12',
            {
                'class': 'people_import_personal_contacts_csv_result',
                'failed': result['failed'],
                'created_count': len(result['created'])
            }
        )
