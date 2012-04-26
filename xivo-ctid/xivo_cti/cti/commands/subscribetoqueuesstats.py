from xivo_cti.cti.cti_command import CTICommand
from xivo_cti.cti.cti_command_factory import CTICommandFactory


class SubscribeToQueuesStats(CTICommand):

    COMMAND_CLASS = 'subscribetoqueuesstats'

    required_fields = [CTICommand.CLASS]
    conditions = [(CTICommand.CLASS, COMMAND_CLASS)]
    _callbacks = []
    _callbacks_with_params = []

    def __init__(self):
        super(SubscribeToQueuesStats, self).__init__()

    def _init_from_dict(self, msg):
        super(SubscribeToQueuesStats, self)._init_from_dict(msg)

CTICommandFactory.register_class(SubscribeToQueuesStats)
