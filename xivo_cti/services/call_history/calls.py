# -*- coding: utf-8 -*-

# Copyright (C) 2013-2015 Avencall
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

    def __init__(self, date, duration, caller_name, extension, mode):
        self.date = date
        self.duration = duration
        self.caller_name = caller_name
        self.extension = extension
        self.mode = mode

    def __eq__(self, other):
        return (self.date == other.date
                and self.duration == other.duration
                and self.caller_name == other.caller_name
                and self.extension == other.extension
                and self.mode == other.mode)

    def __ne__(self, other):
        return not self == other
