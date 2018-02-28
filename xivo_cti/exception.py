# -*- coding: utf-8 -*-
# Copyright (C) 2007-2016 Avencall
# SPDX-License-Identifier: GPL-3.0+


class ExtensionInUseError(Exception):
    pass


class InvalidCallbackException(Exception):
    pass


class MissingFieldException(Exception):

    def __init__(self, msg):
        super(MissingFieldException, self).__init__(msg)


class _BaseNoSuchResourceException(LookupError):

    msg = 'No {resource} matching {type}({value})'

    def __str__(self):
        value = super(_BaseNoSuchResourceException, self).__str__()
        return self.msg.format(
            resource=self.resource,
            type=type(value).__name__,
            value=value,
        )


class NoSuchPhoneException(_BaseNoSuchResourceException):

    resource = 'phone'


class NoSuchCallException(Exception):
    pass


class NoSuchExtensionError(Exception):
    pass


class NoSuchLineException(Exception):
    pass


class NoSuchQueueException(Exception):
    pass


class NoSuchUserException(_BaseNoSuchResourceException):

    resource = 'user'


class NoSuchAgentException(Exception):
    pass
