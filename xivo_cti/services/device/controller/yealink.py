# -*- coding: utf-8 -*-
# Copyright (C) 2015 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.helpers.db_utils import session_scope
from xivo_dao import line_dao

from xivo_cti.services.device.controller import base


class YealinkController(base.BaseController):

    def answer(self, device):
        with session_scope():
            peer = line_dao.get_peer_name(device.id)

        xml_content = {
            'Content':
                r'<?xml version=\"1.0\" encoding=\"UTF-8\"?>'
                r'<YealinkIPPhoneExecute Beep=\"no\"><ExecuteItem URI=\"Key:LINE1\"/></YealinkIPPhoneExecute>',
            'Event': 'Yealink-xml',
            'Content-type': 'application/xml',
        }

        self._ami.sipnotify(peer, xml_content)
