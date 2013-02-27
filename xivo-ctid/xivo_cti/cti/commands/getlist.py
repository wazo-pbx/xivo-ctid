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


def _parse(msg, command):
    command.list_name = msg['listname']
    command.item_id = msg.get('tid')


def _new_class(function_name):
    def match(msg):
        return msg['function'] == function_name

    return CTICommandClass('getlist', match, _parse)


ListID = _new_class('listid')
ListID.add_to_getlist_registry('listid')

UpdateConfig = _new_class('updateconfig')
UpdateConfig.add_to_getlist_registry('updateconfig')

UpdateStatus = _new_class('updatestatus')
UpdateStatus.add_to_getlist_registry('updatestatus')
