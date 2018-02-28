# -*- coding: utf-8 -*-
# Copyright (C) 2013-2015 Avencall
# SPDX-License-Identifier: GPL-3.0+


class Call(object):

    def __init__(self, date, duration, caller_name, extension, mode):
        self.date = date
        self.duration = duration
        self.caller_name = caller_name
        self.extension = extension
        self.mode = mode

    def __eq__(self, other):
        return (self.date == other.date and
                self.duration == other.duration and
                self.caller_name == other.caller_name and
                self.extension == other.extension and
                self.mode == other.mode)

    def __ne__(self, other):
        return not self == other
