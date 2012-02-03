import logging

logger = logging.getLogger('CTICommandRunner')


class CTICommandRunner(object):

    def __init__(self):
        pass

    def _get_arguments(self, command, args):
        return [getattr(command, arg) if not callable(getattr(command, arg)) else getattr(command, arg)() for arg in args]

    def run(self, command):
        for callback in command.callbacks_with_params():
            function, args = callback
            arg_list = self._get_arguments(command, args)
            function(*arg_list)
        return {'status': 'OK'}
