from xivo_cti.cti.missing_field_exception import MissingFieldException


class AMIAction(object):

    _required_fields = []  # Required fields to send this action
    _optionnal_dependencies = []  # List of tupple of mutualy exclusive dependencies see originate

    def __init__(self):
        self.action = None
        self.actionid = None

    def _fields_missing(self):
        for field in self.__class__._required_fields:
            if not hasattr(self, field) or not getattr(self, field):
                return True
        return self._optionnal_dependency_missing()

    def _optionnal_dependency_missing(self):
        for dependency_list in self.__class__._optionnal_dependencies:
            missed_field = False
            for field in dependency_list:
                if not hasattr(self, field) or not getattr(self, field):
                    missed_field = True
            if not missed_field:
                return False
        return True

    def _get_args(self):
        if self._fields_missing():
            raise MissingFieldException('Cannot send AMI action %s' % self.action)
        return []

    def send(self, ami):
        return ami.sendcommand(self.action, self._get_args())
