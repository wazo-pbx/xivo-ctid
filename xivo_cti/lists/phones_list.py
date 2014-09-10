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

import logging
import time
from xivo_cti.cti_anylist import ContextAwareAnyList
from xivo.asterisk import protocol_interface
from xivo.asterisk.protocol_interface import InvalidChannelError

logger = logging.getLogger('phonelist')


class PhonesList(ContextAwareAnyList):

    def __init__(self, innerdata):
        self._innerdata = innerdata
        ContextAwareAnyList.__init__(self, 'phones')
        self._phone_id_by_proto_and_name = {}

    def init_data(self):
        super(PhonesList, self).init_data()
        self._init_reverse_dictionaries()

    def add(self, phone_id):
        super(PhonesList, self).add(phone_id)
        self._add_to_reverse_dictionaries(phone_id)

    def delete(self, phone_id):
        self._remove_from_reverse_dictionaries(phone_id)
        super(PhonesList, self).delete(phone_id)

    def _init_reverse_dictionaries(self):
        phone_id_by_proto_and_name = {}
        for phone_id, phone in self.keeplist.iteritems():
            proto_and_name = phone['protocol'] + phone['name']
            phone_id_by_proto_and_name[proto_and_name] = phone_id
        self._phone_id_by_proto_and_name = phone_id_by_proto_and_name

    def _add_to_reverse_dictionaries(self, phone_id):
        phone = self.keeplist[phone_id]
        proto_and_name = phone['protocol'] + phone['name']
        self._phone_id_by_proto_and_name[proto_and_name] = phone_id

    def _remove_from_reverse_dictionaries(self, phone_id):
        phone = self.keeplist[phone_id]
        proto_and_name = phone['protocol'] + phone['name']
        del self._phone_id_by_proto_and_name[proto_and_name]

    def __createorupdate_comm__(self, phoneid, commid, infos):
        comms = self.keeplist[phoneid]['comms']
        if commid in self.keeplist[phoneid]['comms']:
            if 'calleridnum' in infos and comms[commid].get('calleridnum') != infos['calleridnum']:
                logger.debug('  __createorupdate_comm__ changed calleridnum[%s %s] %s => %s',
                             commid, comms[commid].get('thischannel'), comms[commid].get('calleridnum'), infos['calleridnum'])
            self.keeplist[phoneid]['comms'][commid].update(infos)
        elif 'calleridnum' in infos:
            logger.debug('  __createorupdate_comm__ new calleridnum[%s %s] : %s',
                         commid, infos.get('thischannel'), infos['calleridnum'])
            self.keeplist[phoneid]['comms'][commid] = infos
            self.setlinenum(phoneid, commid)

    def setlinenum(self, phoneid, commid):
        """
        Define a line number for the phone, according to the currently 'busy'
        channels/uniqueids.
        This can not (at the time being, at least) be directly related
        to the line numbers on the physical phones.
        """
        usedlines = []
        for cinfo in self.keeplist[phoneid]['comms'].itervalues():
            if 'linenum' in cinfo:
                usedlines.append(cinfo['linenum'])
        linenum = 1
        while (linenum in usedlines):
            linenum += 1
        self.keeplist[phoneid]['comms'][commid]['linenum'] = linenum

    def clear(self, uid):
        phoneidlist = []
        for phoneid, phoneprops in self.keeplist.iteritems():
            if uid in phoneprops['comms']:
                del phoneprops['comms'][uid]
                if phoneid not in phoneidlist:
                    phoneidlist.append(phoneid)
        return phoneidlist

    def setdisplayhints(self, dh):
        self.display_hints = dh

    def status(self, phoneid):
        tosend = {}
        if phoneid in self.keeplist:
            tosend = {'class': 'phones',
                      'direction': 'client',
                      'function': 'update',
                      'phoneid': phoneid,
                      'status': self.keeplist[phoneid]}
        return tosend

    def ami_meetmejoin(self, phoneid, uid, meetmenum):
        if phoneid in self.keeplist:
            if uid in self.keeplist[phoneid]['comms']:
                infos = {'timestamp-link': time.time(),
                         'calleridname': '<meetme>',
                         'calleridnum': meetmenum}
                self.keeplist[phoneid]['comms'][uid].update(infos)

    def find_phone_by_channel(self, channel):
        try:
            proto_iface = protocol_interface.protocol_interface_from_channel(channel)
        except InvalidChannelError:
            return None
        phone_id = self.get_phone_id_from_proto_and_name(proto_iface.protocol.lower(), proto_iface.interface)

        if phone_id is None:
            return None
        else:
            return self.keeplist[phone_id]

    def get_main_line(self, user_id):
        users_phones = [phone for phone in self.keeplist.itervalues() if int(phone['iduserfeatures']) == int(user_id)]
        return users_phones[0] if users_phones else None

    def get_phone_id_from_proto_and_name(self, proto, name):
        proto_and_name = proto + name
        return self._phone_id_by_proto_and_name.get(proto_and_name)

    def get_callerid_from_phone_id(self, phone_id):
        phone = self.keeplist[phone_id]
        protocol = phone['protocol']
        if protocol == 'sccp':
            return self._compute_callerid_for_sccp_phone(phone)
        else:
            return phone['callerid']

    def _compute_callerid_for_sccp_phone(self, phone):
        return '"%s" <%s>' % (phone['cid_name'], phone['cid_num'])
