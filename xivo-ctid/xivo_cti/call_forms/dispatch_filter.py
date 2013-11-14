# -*- coding: utf-8 -*-

# Copyright (C) 2007-2013 Avencall
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


class DispatchFilter(object):

    def __init__(self, innerdata):
        self._innerdata = innerdata
        self._calls_to_user = {}
        self._linked_calls = []

    def handle_agent_complete(self, uniqueid, channel_name):
        self._dispatch('unlink', channel_name)

    def handle_agent_connect(self, uniqueid, channel_name):
        self._dispatch('link', channel_name)

    def handle_bridge(self, uniqueid, channel_name):
        if self._is_calling_a_user(uniqueid) and not self._is_already_linked(uniqueid):
            self._linked_calls.append(uniqueid)
            self._dispatch('link', channel_name)

    def handle_did(self, uniqueid, channel_name):
        self._dispatch('incomingdid', channel_name)

    def handle_group(self, uniqueid, channel_name):
        self._dispatch('dial', channel_name)

    def handle_hangup(self, uniqueid, channel_name):
        self._clean_uniqueid(uniqueid)
        self._dispatch('hangup', channel_name)

    def handle_queue(self, uniqueid, channel_name):
        self._dispatch('dial', channel_name)

    def handle_user(self, uniqueid, channel_name):
        self._calls_to_user[uniqueid] = True
        self._dispatch('dial', channel_name)

    def _clean_uniqueid(self, uniqueid):
        if uniqueid in self._linked_calls:
            self._linked_calls.remove(uniqueid)
        if uniqueid in self._calls_to_user:
            del self._calls_to_user[uniqueid]

    def _dispatch(self, event_name, channel_name):
        self._innerdata.sheetsend(event_name, channel_name)

    def _is_already_linked(self, uniqueid):
        return uniqueid in self._linked_calls

    def _is_calling_a_user(self, uniqueid):
        return self._calls_to_user.get(uniqueid, False)
