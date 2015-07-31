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

from xivo_cti.interfaces import interfaces

import logging
import time

logger = logging.getLogger('interface_info')

infohelptext = ['',
                'help                     : this help',
                '-- informations about misc lists --',
                'showlist [listname [id]] : show all lists or the specified list'
                '-- slightly advanced features --',
                'disc <ip> <port>             : closes the socket linked to <ip>:<port> if present',
                '']


class INFO(interfaces.Interfaces):

    kind = 'INFO'
    sep = '\n'

    def disconnected(self, cause):
        self.connid.sendall('-- disconnected message from server at %s : %s\n' % (time.asctime(), cause))
        interfaces.Interfaces.disconnected(self, cause)

    def manage_connection(self, msg):
        """
        Handles INFO connections (basic administration console,
        primarily aimed at displaying informations first).
        """
        multimsg = msg.replace('\r', '').split(self.sep)
        clireply = []

        for iusefulmsg in multimsg:
            usefulmsg = iusefulmsg.strip()
            if not usefulmsg:
                break
            try:
                retstr = 'OK'
                if usefulmsg == 'help':
                    clireply.extend(infohelptext)

                elif usefulmsg.startswith('showlist'):
                    args = usefulmsg.split()
                    safe = self._ctiserver.safe
                    clireply.append('ipbxid : %s' % self._ctiserver.myipbxid)
                    for k, v in safe.xod_config.iteritems():
                        if len(args) > 1 and not args[1] in k:
                            continue
                        clireply.append('    %s' % k)
                        for kk, vv in v.keeplist.iteritems():
                            if len(args) > 2 and kk not in args[2]:
                                continue
                            listname, list_id = k, kk
                            clireply.append('        %s %s' %
                                            (listname, list_id))
                            clireply.append('        config: \n%s' % vv)
                            try:
                                clireply.append('        status:\n%s' %
                                                safe.xod_status[listname][list_id])
                            except KeyError:
                                clireply.append('        status: None')

                elif usefulmsg.startswith('disc '):
                    command_args = usefulmsg.split()
                    if len(command_args) > 2:
                        ipdef = tuple([command_args[1], int(command_args[2])])
                        socktoremove = None
                        for sockid in self._ctiserver.fdlist_interface_cti:
                            if ipdef == sockid.getpeername():
                                socktoremove = sockid
                        if socktoremove:
                            clireply.append('disconnecting %s (%s)'
                                           % (socktoremove.getpeername(),
                                              self._ctiserver.fdlist_interface_cti[socktoremove]))
                            socktoremove.close()
                            del self._ctiserver.fdlist_interface_cti[socktoremove]
                        else:
                            clireply.append('nobody disconnected')

                else:
                    retstr = 'KO'

                clireply.append('XIVO-INFO:%s' % retstr)
            except Exception:
                logger.exception('INFO connection [%s] : KO when defining for %s',
                                 usefulmsg, self.requester)

        freply = [{'message': clireply}]
        return freply

    def reply(self, replylines):
        try:
            for replyline in replylines:
                self.connid.sendall('%s\n' % replyline)
        except Exception:
            logger.exception('INFO connection [%s] : KO when sending to %s',
                             replylines, self.requester)
