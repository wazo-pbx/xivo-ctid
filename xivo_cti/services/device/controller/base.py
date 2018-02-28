# -*- coding: utf-8 -*-
# Copyright (C) 2007-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+


class BaseController(object):

    def __init__(self, ami):
        self._ami = ami

    def answer(self, device):
        return
