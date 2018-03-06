# -*- coding: utf-8 -*-
# Copyright (C) 2007-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

import logging

logger = logging.getLogger(__name__)


class VoicemailDAO(object):

    def __init__(self, innerdata):
        self.innerdata = innerdata

    def get_number(self, vm_id):
        vm = self.innerdata.xod_config['voicemails'].keeplist[vm_id]
        return vm['mailbox']
