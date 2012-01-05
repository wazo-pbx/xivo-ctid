from xivo_cti.cti.cti_command import CTICommand


class InviteConfroom(CTICommand):

    required_fields = ['class', 'invitee']

    def __init__(self, msg):
        super(InviteConfroom, self).__init__(msg)
        self._invitee = msg['invitee']
