# -*- coding: utf-8 -*-

# vim: set fileencoding=utf-8 :
# xivo-ctid

# Copyright (C) 2007-2011  Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Pro-formatique SARL. See the LICENSE file at top of the
# source tree or delivered in the installable package in which XiVO CTI Server
# is distributed for more details.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

class QueueStatisticsEncoder(object):

    def encode(self, statistics):
        res = {}
        for queue_name, statistic in statistics.iteritems():
            res[queue_name] = {'Xivo-Join': statistic.received_call_count,
                               'Xivo-Link': statistic.answered_call_count,
                               'Xivo-Lost': statistic.abandonned_call_count,
                               'Xivo-Rate': statistic.efficiency,
                               'Xivo-Qos': statistic.qos,
                               'Xivo-Holdtime-max': statistic.max_hold_time
                               }
        return {'stats': res}
