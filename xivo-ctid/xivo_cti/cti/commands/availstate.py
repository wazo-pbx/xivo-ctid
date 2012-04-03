from xivo_cti.cti.cti_command import CTICommand
from xivo_cti.cti.cti_command_factory import CTICommandFactory


class Availstate(CTICommand):

    COMMAND_CLASS = 'availstate'
    AVAILSTATE = 'availstate'

    required_fields = [CTICommand.CLASS, AVAILSTATE]
    conditions = [(CTICommand.CLASS, COMMAND_CLASS)]
    _callbacks = []
    _callbacks_with_params = []

    def __init__(self):
        super(Availstate, self).__init__()
        self.availstate = None

    def _init_from_dict(self, msg):
        super(Availstate, self)._init_from_dict(msg)
        self.availstate = msg[self.AVAILSTATE]

CTICommandFactory.register_class(Availstate)
