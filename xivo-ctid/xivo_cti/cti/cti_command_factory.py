class CTICommandFactory(object):

    _registered_classes = set()

    def get_command(self, msg):
        return [klass for klass in self.__class__._registered_classes if klass.match_message(msg)]

    @classmethod
    def register_class(cls, klass_to_register):
        cls._registered_classes.add(klass_to_register)
