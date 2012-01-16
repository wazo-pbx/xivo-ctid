from xivo_cti.cti.cti_command import CTICommand
from xivo_cti.cti.cti_command_factory import CTICommandFactory


class LoginID(CTICommand):

    COMMAND_CLASS = 'login_id'

    COMPANY = 'company'
    GIT_DATE = 'git_date'
    GIT_HASH = 'git_hash'
    IDENT = 'ident'
    LASTLOGOUT_DATETIME = 'lastlogout-datetime'
    LASTLOGOUT_STOPPER = 'lastlogout-stopper'
    USERLOGIN = 'userlogin'
    VERSION = 'version'
    XIVO_VERSION = 'xivoversion'
    SESSIONID = 'sessionid'

    required_fields = [CTICommand.CLASS, USERLOGIN, IDENT, COMPANY, GIT_DATE, GIT_HASH, XIVO_VERSION]
    conditions = [(CTICommand.CLASS, COMMAND_CLASS)]
    _callbacks = []

    def __init__(self):
        super(LoginID, self).__init__()
        self.command_class = self.COMMAND_CLASS
        self.company = None
        self.git_date = None
        self.git_hash = None
        self.ident = None
        self.lastlogout_datetime = None
        self.lastlogout_stopper = None
        self.userlogin = None
        self.version = None
        self.xivo_version = None

    def _init_from_dict(self, msg):
        super(LoginID, self)._init_from_dict(msg)
        self.company = msg[self.COMPANY]
        self.git_date = msg[self.GIT_DATE]
        self.git_hash = msg[self.GIT_HASH]
        self.ident = msg[self.IDENT]
        self.lastlogout_datetime = msg.get(self.LASTLOGOUT_DATETIME)
        self.lastlogout_stopper = msg.get(self.LASTLOGOUT_STOPPER)
        self.userlogin = msg[self.USERLOGIN]
        self.version = msg.get(self.VERSION)
        self.xivo_version = msg[self.XIVO_VERSION]

    def get_reply_ok(self, session_id):
        return {self.CLASS: self.COMMAND_CLASS,
                self.REPLYID: self.commandid,
                self.SESSIONID: session_id,
                self.VERSION: self.version,
                self.XIVO_VERSION: self.xivo_version}


CTICommandFactory.register_class(LoginID)
