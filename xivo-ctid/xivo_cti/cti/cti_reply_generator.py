class CTIReplyGenerator(object):

    def get_reply(self, message_type, command, message, close_connection=False):
        return {'message': message,
                'replyid': command.commandid,
                'class': command.command_class,
                'closemenow': close_connection}
