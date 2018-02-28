# -*- coding: utf-8 -*-
# Copyright (C) 2007-2015 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao import line_dao
from xivo_cti.services.device.controller import base


class AastraController(base.BaseController):

    def answer(self, device):
        peer = line_dao.get_peer_name(device.id)
        xml_content = {
            'Content': r'<AastraIPPhoneExecute><ExecuteItem URI=\"Key:Line1\"/></AastraIPPhoneExecute>',
            'Event': 'aastra-xml',
            'Content-type': 'application/xml',
        }
        self._ami.sipnotify(peer, xml_content)
