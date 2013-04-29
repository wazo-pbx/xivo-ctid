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


def _match(msg):
    return msg.get('command') == 'dial'


def _parse(msg, command):
    destination = msg.get('destination')
    if 'exten:xivo/' in destination:
        command.exten = destination.split('/', 1)[1]
    else:
        command.exten = destination


Dial = CTICommandClass('ipbxcommand', _match, _parse)
Dial.add_to_registry()
