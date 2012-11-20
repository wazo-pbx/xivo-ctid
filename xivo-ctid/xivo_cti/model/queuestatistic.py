# -*- coding: UTF-8 -*-

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
