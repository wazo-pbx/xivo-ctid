# -*- coding: utf-8 -*-

# Copyright (C) 2013 Avencall
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


class Call(object):

    def __init__(self, source, destination):
        self.source = source
        self.destination = destination

    @property
    def is_internal(self):
        return self.source.is_internal and self.destination.is_internal

    def __eq__(self, compared_call):
        return self._is_equal(compared_call)

    def __ne__(self, compared_call):
        return not self._is_equal(compared_call)

    def _is_equal(self, compared_call):
        return (self.source == compared_call.source and
                self.destination == compared_call.destination)
