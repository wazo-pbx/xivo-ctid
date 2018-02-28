# -*- coding: utf-8 -*-
# Copyright (C) 2007-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+


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
