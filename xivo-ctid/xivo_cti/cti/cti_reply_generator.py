class CTIReplyGenerator(object):

    def get_reply(self, message_type, command, message, close_connection=False):
        ret = {'message': message,
               'replyid': command.commandid,
               'class': command.command_class}
        if close_connection:
            ret['closemenow'] = True
        return ret
