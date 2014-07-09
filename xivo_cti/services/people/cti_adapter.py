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

from xivo_cti import dao
from xivo_cti.cti.cti_message_formatter import CTIMessageFormatter


class PeopleCTIAdapter(object):

    def __init__(self, dird, cti_server):
        self._dird = dird
        self._cti_server = cti_server

    def get_headers(self, user_id):
        profile = dao.user.get_context(user_id)
        self._dird.headers(profile, self.send_headers_result, user_id)

    def send_headers_result(self, user_id, headers):
        xuserid = 'xivo/{user_id}'.format(user_id=user_id)
        message = CTIMessageFormatter.people_headers_result(headers)
        self._cti_server.send_to_cti_client(xuserid, message)
