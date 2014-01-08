# -*- coding: utf-8 -*-

# Copyright (C) 2007-2014 Avencall
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


class QueueStatisticsEncoder(object):

    def encode(self, statistics):
        res = {}
        for queue_name, statistic in statistics.iteritems():
            res[queue_name] = {'Xivo-Join': '%s' % statistic.received_call_count,
                               'Xivo-Link': '%s' % statistic.answered_call_count,
                               'Xivo-Lost': '%s' % statistic.abandonned_call_count,
                               'Xivo-Rate': '%s' % statistic.efficiency,
                               'Xivo-Qos': '%s' % statistic.qos,
                               'Xivo-Holdtime-avg': '%s' % statistic.mean_hold_time,
                               'Xivo-Holdtime-max': '%s' % statistic.max_hold_time
                               }
        return {'stats': res}
