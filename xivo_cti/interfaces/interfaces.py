# -*- coding: utf-8 -*-

# Copyright (C) 2007-2014 Avencall
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


class DisconnectCause(object):

    by_client = 'by_client'
    by_server_stop = 'by_server_stop'
    by_server_reload = 'by_server_reload'
    broken_pipe = 'broken_pipe'


class Interfaces(object):
    DisconnectCause = DisconnectCause

    def __init__(self, ctiserver):
        self._ctiserver = ctiserver
        self.connid = None
        self.requester = None

    def connected(self, connid):
        self.connid = connid
        self.requester = connid.getpeername()[:2]

    def disconnected(self, cause):
        self.connid = None
        self.requester = None
