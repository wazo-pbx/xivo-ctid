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

from xivo_cti.cti.cti_command import CTICommandClass


class HistoryMode(object):
    answered = '1'
    missed = '2'
    outgoing = '0'


def _parse(msg, command):
    command.mode = _mode(msg['mode'])
    command.size = int(msg['size'])


def _mode(mode):
    if mode == '0':
        return HistoryMode.outgoing
    elif mode == '1':
        return HistoryMode.answered
    elif mode == '2':
        return HistoryMode.missed


History = CTICommandClass('history', None, _parse)
History.add_to_registry()
