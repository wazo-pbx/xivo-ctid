# -*- coding: utf-8 -*-
# Copyright (C) 2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

import logging

logger = logging.getLogger(__name__)


class Task(object):

    def __init__(self, function, args):
        self._function = function
        self._args = args

    def run(self):
        try:
            self._function(*self._args)
        except Exception:
            logger.exception('Unexpected exception raised while running task')
