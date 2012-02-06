from xivo_cti.cti.cti_command import CTICommand
from xivo_cti.cti.cti_command_factory import CTICommandFactory
from xivo_cti.cti.commands.set_user_service import SetUserService
from xivo_cti.cti.commands.user_service.set_forward import SetForward


class DisableBusyForward(SetForward):

    FUNCTION_NAME = 'fwd'
    ENABLE_NAME = 'enablebusy'
    DESTINATION_NAME = 'destbusy'

    required_fields = [CTICommand.CLASS, SetUserService.FUNCTION, SetUserService.VALUE]
    conditions = [(CTICommand.CLASS, SetUserService.COMMAND_CLASS),
                  (SetUserService.FUNCTION, FUNCTION_NAME),
                  ((SetUserService.VALUE, ENABLE_NAME), False)]
    _callbacks_with_params = []

CTICommandFactory.register_class(DisableBusyForward)
