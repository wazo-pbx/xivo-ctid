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

from xivo_cti.cti.cti_command_factory import CTICommandFactory
from xivo_cti.cti.cti_command_runner import CTICommandRunner


class CTICommandHandler(object):

    def __init__(self, cti_connection):
        self._command_factory = CTICommandFactory()
        self._cti_connection = cti_connection
        self._commands_to_run = []
        self._command_runner = CTICommandRunner()

    def parse_message(self, message):
        command_classes = self._command_factory.get_command(message)
        for command_class in command_classes:
            self._commands_to_run.append(command_class.from_dict(message))

    def run_commands(self):
        return_values = []
        while self._commands_to_run:
            command = self._commands_to_run.pop()
            if not command.cti_connection:
                command.cti_connection = self._cti_connection
            return_values.append(self._command_runner.run(command))
        return [return_value for return_value in return_values if return_value]
