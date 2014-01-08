# -*- coding: utf-8 -*-

# Copyright (C) 2013-2014 Avencall
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


def _new_class(function_name, value):

    def match(msg):
        return msg['function'] == function_name and msg['value'] == value

    def parse(msg, command):
        command.target = msg.get('target')

    return CTICommandClass('featuresput', match, parse)


EnableDND = _new_class('enablednd', True)
EnableDND.add_to_registry()

DisableDND = _new_class('enablednd', False)
DisableDND.add_to_registry()

EnableFilter = _new_class('incallfilter', True)
EnableFilter.add_to_registry()

DisableFilter = _new_class('incallfilter', False)
DisableFilter.add_to_registry()

EnableRecording = _new_class('enablerecording', True)
EnableRecording.add_to_registry()

DisableRecording = _new_class('enablerecording', False)
DisableRecording.add_to_registry()
