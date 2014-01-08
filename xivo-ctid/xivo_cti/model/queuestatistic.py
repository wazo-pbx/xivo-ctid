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

NO_VALUE = ""


class QueueStatistic(object):

    def __init__(self):
        self.received_call_count = 0
        self.answered_call_count = 0
        self.abandonned_call_count = 0
        self.max_hold_time = 0
        self.efficiency = NO_VALUE
        self.qos = NO_VALUE
        self.mean_hold_time = NO_VALUE
