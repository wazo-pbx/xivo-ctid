from xivo_cti.cti.commands.set_user_service import SetUserService


class SetForward(SetUserService):

    FUNCTION_NAME = 'fwd'
    ENABLE_NAME = 'enablename'
    DESTINATION_NAME = 'destname'

    def _init_from_dict(self, msg):
        super(SetForward, self)._init_from_dict(msg)
        self.destination = msg[SetUserService.VALUE][self.DESTINATION_NAME]
        self.enable = msg[SetUserService.VALUE][self.ENABLE_NAME]

