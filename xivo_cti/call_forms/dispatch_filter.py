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


class DispatchFilter(object):

    def __init__(self, innerdata):
        self._innerdata = innerdata
        self._calls_to_user = {}
        self._linked_calls = []

    def handle_agent_called(self, uniqueid):
        self._dispatch('dial', uniqueid)

    def handle_agent_complete(self, uniqueid):
        self._dispatch('unlink', uniqueid)

    def handle_agent_connect(self, uniqueid):
        self._dispatch('link', uniqueid)

    def handle_bridge_link(self, bridge_event):
        channel = bridge_event.bridge.get_caller_channel()
        self._handle_bridge(channel.unique_id)

    def _handle_bridge(self, uniqueid):
        if self._is_calling_a_user(uniqueid) and not self._is_already_linked(uniqueid):
            self._linked_calls.append(uniqueid)
            self._dispatch('link', uniqueid)

    def handle_dial(self, uniqueid, _channel_name):
        if self._is_calling_a_user(uniqueid):
            self._dispatch('dial', uniqueid)

    def handle_did(self, uniqueid, _channel_name):
        self._dispatch('incomingdid', uniqueid)

    def handle_hangup(self, uniqueid, channel_name):
        self._clean_uniqueid(uniqueid)
        if 'agentcallback' in channel_name:
            return
        self._dispatch('hangup', uniqueid)

    def handle_user(self, uniqueid, _channel_name):
        self._calls_to_user[uniqueid] = True

    def _clean_uniqueid(self, uniqueid):
        if uniqueid in self._linked_calls:
            self._linked_calls.remove(uniqueid)
        if uniqueid in self._calls_to_user:
            del self._calls_to_user[uniqueid]

    def _dispatch(self, event_name, uniqueid):
        self._innerdata.sheetsend(event_name, uniqueid)

    def _is_already_linked(self, uniqueid):
        return uniqueid in self._linked_calls

    def _is_calling_a_user(self, uniqueid):
        return self._calls_to_user.get(uniqueid, False)
