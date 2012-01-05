from xivo_cti.cti.cti_command import CTICommand
from xivo_cti.cti.cti_command_factory import CTICommandFactory


class InviteConfroom(CTICommand):

    required_fields = ['class', 'invitee']
    conditions = [('class', 'invite_confroom')]

    def __init__(self, msg):
        super(InviteConfroom, self).__init__(msg)
        self._invitee = msg['invitee']

CTICommandFactory.register_class(InviteConfroom)
