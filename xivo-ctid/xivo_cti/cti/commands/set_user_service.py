from xivo_cti.cti.cti_command import CTICommand


class SetUserService(CTICommand):

    COMMAND_CLASS = 'featuresput'

    FUNCTION = 'function'
    VALUE = 'value'

    required_fields = [CTICommand.CLASS, FUNCTION, VALUE]
    conditions = [(CTICommand.CLASS, COMMAND_CLASS)]
    _callbacks = []
    _callbacks_with_params = []

    def _init_from_dict(self, msg):
        super(SetUserService, self)._init_from_dict(msg)
        self.function = msg[self.FUNCTION]
        self.value = msg[self.VALUE]
