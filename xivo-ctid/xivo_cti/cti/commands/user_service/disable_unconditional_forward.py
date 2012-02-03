from xivo_cti.cti.cti_command import CTICommand
from xivo_cti.cti.cti_command_factory import CTICommandFactory
from xivo_cti.cti.commands.set_user_service import SetUserService


class DisableUnconditionalForward(SetUserService):

    FUNCTION_NAME = 'fwd'
    ENABLE_NAME = 'enableunc'
    DESTINATION = 'destunc'

    required_fields = [CTICommand.CLASS, SetUserService.FUNCTION, SetUserService.VALUE]
    conditions = [(CTICommand.CLASS, SetUserService.COMMAND_CLASS),
                  (SetUserService.FUNCTION, FUNCTION_NAME),
                  ((SetUserService.VALUE,ENABLE_NAME), False)]
    _callbacks = []
    _callbacks_with_params = []
    
    
    def _init_from_dict(self, msg):
        super(DisableUnconditionalForward, self)._init_from_dict(msg)
        self.destination = msg[SetUserService.VALUE][self.DESTINATION]
        self.enable = msg[SetUserService.VALUE][self.ENABLE_NAME]


CTICommandFactory.register_class(DisableUnconditionalForward)
