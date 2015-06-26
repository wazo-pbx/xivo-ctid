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

    def set_favorite(self, cti_connection, user_id, directory, contact, enabled):
        logger.debug('Set Favorite called')
        token = cti_connection.connection_details['auth_token']
        callback = partial(self._send_set_favorite_result, user_id, directory, contact, enabled)

        if enabled:
            function = self._client.directories.new_favorite
        else:
            function = self._client.directories.remove_favorite

        self._runner.run_with_cb(callback, function, directory=directory, contact=contact, token=token)

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

    def _send_set_favorite_result(self, user_id, directory, contact, enabled, result):
        xuserid = 'xivo/{user_id}'.format(user_id=user_id)
        message = CTIMessageFormatter.people_set_favorite_result(directory, contact, enabled)
        self._cti_server.send_to_cti_client(xuserid, message)
