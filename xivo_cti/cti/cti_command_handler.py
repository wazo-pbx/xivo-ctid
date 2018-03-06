# -*- coding: utf-8 -*-
# Copyright (C) 2007-2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_cti.cti import cti_command_registry
from xivo_cti.cti.cti_command_runner import CTICommandRunner


class CTICommandHandler(object):

    def __init__(self, cti_connection):
        self._cti_connection = cti_connection
        self._commands_to_run = []
        self._command_runner = CTICommandRunner()

    def parse_message(self, message):
        command_classes = cti_command_registry.get_class(message)
        for command_class in command_classes:
            command = command_class.from_dict(message)
            command.cti_connection = self._cti_connection
            command.user_id = self._cti_connection.connection_details.get('userid')
            command.user_uuid = self._cti_connection.connection_details.get('user_uuid')
            command.auth_token = self._cti_connection.connection_details.get('auth_token')
            self._commands_to_run.append(command)

    def run_commands(self):
        return_values = []
        while self._commands_to_run:
            command = self._commands_to_run.pop()
            return_values.append(self._command_runner.run(command))
        return [return_value for return_value in return_values if return_value]
