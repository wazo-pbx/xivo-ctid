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


class HistoryCall(object):
    def __init__(self):
        raise NotImplementedError()

    def display_other_end(self):
        raise NotImplementedError()


class ReceivedCall(HistoryCall):
    def __init__(self, date, duration, caller_name, extension):
        self.date = date
        self.duration = duration
        self.caller_name = caller_name
        self.extension = extension

    def display_other_end(self):
        return self.caller_name

    def __eq__(self, other):
        return (self.date == other.date
                and self.duration == other.duration
                and self.caller_name == other.caller_name
                and self.exten == other.exten)

    def __ne__(self, other):
        return not self == other


class SentCall(HistoryCall):
    def __init__(self, date, duration, extension):
        self.date = date
        self.duration = duration
        self.extension = extension

    def display_other_end(self):
        return self.extension

    def __eq__(self, other):
        return (self.date == other.date
                and self.duration == other.duration
                and self.extension == other.extension)

    def __ne__(self, other):
        return not self == other
