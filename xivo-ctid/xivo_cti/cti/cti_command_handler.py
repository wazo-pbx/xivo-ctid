from xivo_cti.cti.cti_command_factory import CTICommandFactory


class CTICommandHandler(object):

    def __init__(self, cti_connection):
        self._command_factory = CTICommandFactory()
        self._cti_connection = cti_connection
        self._commands_to_run = []

    def parse_message(self, message):
        command_classes = self._command_factory.get_command(message)
        for command_class in command_classes:
            self._commands_to_run.append(command_class(message))

    def run_commands(self):
        functions = []
        for command in self._commands_to_run:
            if not command.cti_connection:
                command.cti_connection = self._cti_connection
            functions.extend(command.callbacks)
        return_values = [function(command) for function in functions]
        return [return_value for return_value in return_values if return_value]
