# -*- coding: UTF-8 -*-

# XiVO CTI Server
#
# Copyright (C) 2007-2012  Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Avencall. See the LICENSE file at top of the source tree
# or delivered in the installable package in which XiVO CTI Server is
# distributed for more details.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License

from datetime import datetime
from xivo_cti.services.queue_member import common


class QueueMember(object):

    def __init__(self, queue_name, member_name, state):
        self.id = common.format_queue_member_id(queue_name, member_name)
        self.queue_name = queue_name
        self.member_name = member_name
        self.state = state

    def is_agent(self):
        return common.is_agent_member_name(self.member_name)

    def to_cti_config(self):
        return self._to_cti()

    def to_cti_status(self):
        return self._to_cti()

    def _to_cti(self):
        result = {
            'queue_name': self.queue_name,
            'interface': self.member_name,
            'membership': 'static',
        }
        self.state._to_cti(result)
        return result

    @classmethod
    def from_dao_queue_member(cls, dao_queue_member):
        queue_name = dao_queue_member.queue_name
        member_name = dao_queue_member.member_name
        state = QueueMemberState.from_dao_queue_member(dao_queue_member)
        if common.is_agent_member_name(member_name):
            state.update_as_unlogged_agent()
        return cls(queue_name, member_name, state)


class QueueMemberState(object):

    STATUS_UNKNOWN = '100'
    STATUS_NOT_LOGGED = '101'

    def __init__(self):
        self.calls_taken = 0
        self.interface = None
        self.last_call = None
        self.paused = False
        self.penalty = 0
        self.status = self.STATUS_UNKNOWN

    def copy(self):
        copy = QueueMemberState()
        copy.__dict__ = dict(self.__dict__)
        return copy

    def update_as_unlogged_agent(self):
        self.status = self.STATUS_NOT_LOGGED
        self.paused = False

    def _to_cti(self, result):
        result.update({
            'callstaken': str(self.calls_taken),
            'paused': '1' if self.paused else '0',
            'penalty': str(self.penalty),
            'status': self.status,
        })
        if self.last_call:
            result['lastcall'] = self.last_call.strftime('%H:%M:%S')
        else:
            result['lastcall'] = ''

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return self.__dict__ != other.__dict__

    @classmethod
    def from_ami_queue_member(cls, ami_event):
        state = cls()
        state.calls_taken = int(ami_event['CallsTaken'])
        state.interface = ami_event['Location']
        state.last_call = _convert_last_call(ami_event['LastCall'])
        state.paused = _convert_paused(ami_event['Paused'])
        state.penalty = int(ami_event['Penalty'])
        state.status = ami_event['Status']
        return state

    @classmethod
    def from_ami_queue_member_status(cls, ami_event):
        return cls.from_ami_queue_member(ami_event)

    @classmethod
    def from_ami_queue_member_added(cls, ami_event):
        return cls.from_ami_queue_member(ami_event)

    @classmethod
    def from_dao_queue_member(cls, dao_queue_member):
        state = cls()
        state.penalty = dao_queue_member.penalty
        return state


def _convert_last_call(ami_last_call):
    if ami_last_call == '0':
        return None
    else:
        return datetime.fromtimestamp(int(ami_last_call))


def _convert_paused(ami_paused):
    return bool(int(ami_paused))
