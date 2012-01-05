class MissingFieldException(Exception):

    def __init__(self, msg):
        super(MissingFieldException, self).__init__(msg)
