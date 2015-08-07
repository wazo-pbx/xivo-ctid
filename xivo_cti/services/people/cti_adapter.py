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

import logging

from functools import partial
from xivo_dird_client import Client

from xivo_cti import config
from xivo_cti import dao
from xivo_cti.cti.cti_message_formatter import CTIMessageFormatter

logger = logging.getLogger(__name__)


class PeopleCTIAdapter(object):

    def __init__(self, async_runner, cti_server):
        self._client = Client(**config['dird'])
        self._cti_server = cti_server
        self._runner = async_runner

    def get_headers(self, cti_connection, user_id):
        logger.debug('Get headers called')
        profile = dao.user.get_context(user_id)
        token = cti_connection.connection_details['auth_token']
        callback = partial(self._send_headers_result, user_id)
        self._runner.run_with_cb(callback, self._client.directories.headers, profile=profile, token=token)

    def search(self, cti_connection, user_id, term):
        logger.debug('Search called')
        profile = dao.user.get_context(user_id)
        token = cti_connection.connection_details['auth_token']
        callback = partial(self._send_lookup_result, user_id)
        self._runner.run_with_cb(callback, self._client.directories.lookup, profile=profile, term=term, token=token)

    def favorites(self, cti_connection, user_id):
        logger.debug('Favorites called')
        profile = dao.user.get_context(user_id)
        token = cti_connection.connection_details['auth_token']
        callback = partial(self._send_favorites_result, user_id)
        self._runner.run_with_cb(callback, self._client.directories.favorites, profile=profile, token=token)

    def set_favorite(self, cti_connection, user_id, source, source_entry_id, enabled):
        logger.debug('Set Favorite called')
        token = cti_connection.connection_details['auth_token']
        callback = partial(self._send_favorite_update, user_id, source, source_entry_id, enabled)

        if enabled:
            function = self._client.directories.new_favorite
        else:
            function = self._client.directories.remove_favorite

        self._runner.run_with_cb(callback, function, directory=source, contact=source_entry_id, token=token)

    def personal_contacts(self, cti_connection, user_id):
        logger.debug('Personal Contacts called')
        profile = dao.user.get_context(user_id)
        token = cti_connection.connection_details['auth_token']
        callback = partial(self._send_personal_contacts_result, user_id)
        self._runner.run_with_cb(callback, self._client.directories.personal, profile=profile, token=token)

    def personal_contact_raw(self, cti_connection, user_id, source, source_entry_id):
        logger.debug('Personal Contact called')
        token = cti_connection.connection_details['auth_token']
        callback = partial(self._send_personal_contact_raw_result, user_id, source, source_entry_id)
        self._runner.run_with_cb(callback, self._client.personal.get, contact_id=source_entry_id, token=token)

    def create_personal_contact(self, cti_connection, user_id, contact_infos):
        logger.debug('Create Personal Contact called')
        token = cti_connection.connection_details['auth_token']
        callback = partial(self._send_personal_contact_created, user_id)
        self._runner.run_with_cb(callback, self._client.personal.create, contact_infos=contact_infos, token=token)

    def delete_personal_contact(self, cti_connection, user_id, source, source_entry_id):
        logger.debug('Delete Personal Contact called')
        token = cti_connection.connection_details['auth_token']
        callback = partial(self._send_personal_contact_deleted, user_id, source, source_entry_id)
        self._runner.run_with_cb(callback, self._client.personal.delete, contact_id=source_entry_id, token=token)

    def edit_personal_contact(self, cti_connection, user_id, source, source_entry_id, contact_infos):
        logger.debug('Edit Personal Contact called')
        token = cti_connection.connection_details['auth_token']
        callback = partial(self._send_personal_contact_raw_update,
                           user_id, source, source_entry_id)
        self._runner.run_with_cb(callback, self._client.personal.edit,
                                 contact_id=source_entry_id,
                                 contact_infos=contact_infos,
                                 token=token)

    def import_personal_contacts_csv(self, cti_connection, user_id, csv_contacts):
        logger.debug('Import Personal Contacts CSV called')
        token = cti_connection.connection_details['auth_token']
        callback = partial(self._send_import_personal_contacts_csv_result, user_id)
        self._runner.run_with_cb(callback, self._client.personal.import_csv, csv_text=csv_contacts, token=token)

    def _send_headers_result(self, user_id, headers):
        xuserid = 'xivo/{user_id}'.format(user_id=user_id)
        message = CTIMessageFormatter.people_headers_result(headers)
        self._cti_server.send_to_cti_client(xuserid, message)

    def _send_lookup_result(self, user_id, result):
        xuserid = 'xivo/{user_id}'.format(user_id=user_id)
        message = CTIMessageFormatter.people_search_result(result)
        self._cti_server.send_to_cti_client(xuserid, message)

    def _send_favorites_result(self, user_id, result):
        xuserid = 'xivo/{user_id}'.format(user_id=user_id)
        message = CTIMessageFormatter.people_favorites_result(result)
        self._cti_server.send_to_cti_client(xuserid, message)

    def _send_favorite_update(self, user_id, source, source_entry_id, enabled, result):
        xuserid = 'xivo/{user_id}'.format(user_id=user_id)
        message = CTIMessageFormatter.people_favorite_update(source, source_entry_id, enabled)
        self._cti_server.send_to_cti_client(xuserid, message)

    def _send_personal_contacts_result(self, user_id, result):
        xuserid = 'xivo/{user_id}'.format(user_id=user_id)
        message = CTIMessageFormatter.people_personal_contacts_result(result)
        self._cti_server.send_to_cti_client(xuserid, message)

    def _send_personal_contact_raw_result(self, user_id, source, source_entry_id, result):
        xuserid = 'xivo/{user_id}'.format(user_id=user_id)
        message = CTIMessageFormatter.people_personal_contact_raw_result(source, source_entry_id, result)
        self._cti_server.send_to_cti_client(xuserid, message)

    def _send_personal_contact_created(self, user_id, result):
        xuserid = 'xivo/{user_id}'.format(user_id=user_id)
        message = CTIMessageFormatter.people_personal_contact_created()
        self._cti_server.send_to_cti_client(xuserid, message)

    def _send_personal_contact_deleted(self, user_id, source, source_entry_id, result):
        xuserid = 'xivo/{user_id}'.format(user_id=user_id)
        message = CTIMessageFormatter.people_personal_contact_deleted(source, source_entry_id)
        self._cti_server.send_to_cti_client(xuserid, message)

    def _send_personal_contact_raw_update(self, user_id, source, source_entry_id, result):
        xuserid = 'xivo/{user_id}'.format(user_id=user_id)
        message = CTIMessageFormatter.people_personal_contact_raw_update(source, source_entry_id)
        self._cti_server.send_to_cti_client(xuserid, message)

    def _send_import_personal_contacts_csv_result(self, user_id, result):
        xuserid = 'xivo/{user_id}'.format(user_id=user_id)
        message = CTIMessageFormatter.people_import_personal_contacts_csv_result(result)
        self._cti_server.send_to_cti_client(xuserid, message)
