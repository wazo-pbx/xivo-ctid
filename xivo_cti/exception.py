# -*- coding: utf-8 -*-

# Copyright (C) 2007-2015 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>


class ExtensionInUseError(Exception):
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
