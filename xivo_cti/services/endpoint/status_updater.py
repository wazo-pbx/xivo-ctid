# -*- coding: utf-8 -*-
# Copyright 2014-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import logging

from xivo_cti import dao

logger = logging.getLogger(__name__)


class StatusUpdater(object):

    def __init__(self, endpoint_status_notifier):
        self._notifier = endpoint_status_notifier

    def update_status(self, hint, status):
        # TODO clean after pjsip migration
        hint = hint.replace('PJSIP', 'SIP')
        for phone_id in dao.phone.get_phone_ids_from_hint(hint):
            changed = dao.phone.update_status(phone_id, status)
            if changed:
                self._notifier.notify(phone_id, status)
