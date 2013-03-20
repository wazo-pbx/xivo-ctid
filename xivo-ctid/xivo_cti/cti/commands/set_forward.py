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


def _new_class(enable_name, enable_value, destination_name):

    def match(msg):
        return (
            msg['function'] == 'fwd' and
            enable_name in msg['value'] and
            msg['value'][enable_name] == enable_value
        )

    def parse(msg, command):
        command.destination = msg['value'][destination_name]

    return CTICommandClass('featuresput', match, parse)


EnableBusyForward = _new_class('enablebusy', True, 'destbusy')
EnableBusyForward.add_to_registry()

DisableBusyForward = _new_class('enablebusy', False, 'destbusy')
DisableBusyForward.add_to_registry()

EnableNoAnswerForward = _new_class('enablerna', True, 'destrna')
EnableNoAnswerForward.add_to_registry()

DisableNoAnswerForward = _new_class('enablerna', False, 'destrna')
DisableNoAnswerForward.add_to_registry()

EnableUnconditionalForward = _new_class('enableunc', True, 'destunc')
EnableUnconditionalForward.add_to_registry()

DisableUnconditionalForward = _new_class('enableunc', False, 'destunc')
DisableUnconditionalForward.add_to_registry()
