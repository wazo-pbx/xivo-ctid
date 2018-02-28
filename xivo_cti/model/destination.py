# -*- coding: utf-8 -*-
# Copyright (C) 2013-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

import logging

logger = logging.getLogger(__name__)


class Destination(object):

    def __init__(self, url_type, ipbx, value):
        self.dest_type = url_type
        self.ipbxid = ipbx
        self.value = value

    def __eq__(self, other):
        return (self.dest_type == other.dest_type and
                self.ipbxid == other.ipbxid and
                self.value == other.value)

    def to_exten(self):
        logger.warning('Unimplemented to exten method for type %s', self.dest_type)
