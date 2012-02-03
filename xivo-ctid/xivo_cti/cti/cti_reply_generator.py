class CTIReplyGenerator(object):

    def get_reply(self, message_type, command, message):
        return {'message': message,
                'replyid': command.commandid,
                'class': command.command_class}
