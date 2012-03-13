import logging
from xivo_cti.cti.cti_reply_generator import CTIReplyGenerator

logger = logging.getLogger('CTICommandRunner')


class CTICommandRunner(object):

    def __init__(self):
        self._reply_generator = CTIReplyGenerator()

    def _get_arguments(self, command, args):
        return [getattr(command, arg) if not callable(getattr(command, arg)) else getattr(command, arg)() for arg in args]

    def run(self, command):
        for callback in command.callbacks_with_params():
            function, args = callback
            arg_list = self._get_arguments(command, args)
            reply = function(*arg_list)
            if reply:
                return self._reply_generator.get_reply(reply[0], command, reply[1], reply[2] if len(reply) >= 3 else False)
        return {'status': 'OK'}
