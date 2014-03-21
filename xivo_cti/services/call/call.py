# -*- coding: utf-8 -*-

# Copyright (C) 2013-2014 Avencall
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


class _Channel(object):
    """
    The _Channel class is package private to the call package and it's _private
    fields should not be used outside the package
    """

    def __init__(self, extension, channel):
        self.extension = extension
        self._channel = channel

    def __eq__(self, other):
        return self.extension == other.extension and self._channel == other._channel

    def __repr__(self):
        return '<_Channel %s>' % self.extension


class Call(object):

    def __init__(self, source, destination):
        self.source = source
        self.destination = destination

    def __repr__(self):
        info = {
            'name': self.__class__.__name__,
            'source': self.source.extension,
            'destination': self.destination.extension,
        }
        return '%(name)s from %(source)s to %(destination)s' % info

    @property
    def is_internal(self):
        return (self.source.extension.is_internal
                and self.destination.extension.is_internal)

    def __eq__(self, compared_call):
        return self._is_equal(compared_call)

    def __ne__(self, compared_call):
        return not self._is_equal(compared_call)

    def _is_equal(self, compared_call):
        return (self.source == compared_call.source and
                self.destination == compared_call.destination)
