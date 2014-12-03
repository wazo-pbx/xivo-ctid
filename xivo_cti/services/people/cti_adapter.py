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

import logging

from functools import partial
from xivo_cti import dao
from xivo_cti.cti.cti_message_formatter import CTIMessageFormatter

logger = logging.getLogger(__name__)


class PeopleCTIAdapter(object):

    def __init__(self, async_dird_client, cti_server):
        self._dird = async_dird_client
        self._cti_server = cti_server

    def get_headers(self, user_id):
        logger.debug('Get headers called')
        profile = dao.user.get_context(user_id)
        callback = partial(self._send_headers_result, user_id)
        self._dird.headers(profile, callback)

    def search(self, user_id, term):
        logger.debug('Search called')
        profile = dao.user.get_context(user_id)
        callback = partial(self._send_lookup_result, user_id)
        self._dird.lookup(profile, term, callback)

    def _send_headers_result(self, user_id, headers):
        xuserid = 'xivo/{user_id}'.format(user_id=user_id)
        message = CTIMessageFormatter.people_headers_result(headers)
        self._cti_server.send_to_cti_client(xuserid, message)

    def _send_lookup_result(self, user_id, result):
        xuserid = 'xivo/{user_id}'.format(user_id=user_id)
        message = CTIMessageFormatter.people_search_result(result)
        self._cti_server.send_to_cti_client(xuserid, message)
