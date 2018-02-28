# -*- coding: utf-8 -*-
# Copyright (C) 2013-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

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
