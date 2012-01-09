from xivo_cti.cti.missing_field_exception import MissingFieldException


class CTICommand(object):

    required_fields = ['class']
    conditions = None
    _callbacks = []

    def __init__(self, msg):
        self._msg = msg
        self._check_required_fields()
        self.cti_connection = None
        self._commandid = self._msg.get('commandid')
        self._command_class = self._msg['class']
        self.callbacks = self.__class__._callbacks

    def _check_required_fields(self):
        for field in self.__class__.required_fields:
            if field not in self._msg:
                raise MissingFieldException(u'Missing %s in CTI command' % field)

    def get_reply(self, message_type, message, close_connection=False):
        rep = {'class': self._command_class,
               message_type: {'message': message}}
        if self._commandid:
            rep['replyid'] = self._commandid
        if close_connection:
            rep['closemenow'] = True
        return rep

    def get_warning(self, message, close_connection=False):
        return self.get_reply('warning', message, close_connection)

    def get_message(self, message, close_connection=False):
        return self.get_reply('message', message, close_connection)

    @classmethod
    def match_message(cls, message):
        if not cls.conditions:
            return False
        for (field, value) in cls.conditions:
            try:
                if not message[field] == value:
                    return False
            except KeyError:
                return False
        return True

    @classmethod
    def register_callback(cls, function):
        cls._callbacks.append(function)
