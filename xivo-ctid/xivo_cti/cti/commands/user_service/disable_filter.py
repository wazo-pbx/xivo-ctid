from xivo_cti.cti.cti_command import CTICommand
from xivo_cti.cti.cti_command_factory import CTICommandFactory
from xivo_cti.cti.commands.set_user_service import SetUserService


class DisableFilter(SetUserService):

    FUNCTION_NAME = 'incallfilter'

    required_fields = [CTICommand.CLASS, SetUserService.FUNCTION, SetUserService.VALUE]
    conditions = [(CTICommand.CLASS, SetUserService.COMMAND_CLASS),
                  (SetUserService.FUNCTION, FUNCTION_NAME),
                  (SetUserService.VALUE, False)]
    _callbacks = []
    _callbacks_with_params = []

CTICommandFactory.register_class(DisableFilter)
