# -*- coding: utf-8 -*-

# Copyright (C) 2007-2014 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

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
