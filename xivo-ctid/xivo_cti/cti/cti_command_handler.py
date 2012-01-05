import Queue

from xivo_cti.cti.cti_command_factory import CTICommandFactory


class CTICommandHandler(object):

    def __init__(self):
        self._command_factory = CTICommandFactory()
        self._commands_to_run = Queue.Queue()

    def parse_message(self, message):
        command_classes = self._command_factory.get_command(message)
        for command_class in command_classes:
            self._commands_to_run.put(command_class(message))
