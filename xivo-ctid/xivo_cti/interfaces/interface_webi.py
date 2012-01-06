# vim: set fileencoding=utf-8 :
# XiVO CTI Server
__copyright__ = 'Copyright (C) 2007-2011  Avencall'

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Pro-formatique SARL. See the LICENSE file at top of the
# source tree or delivered in the installable package in which XiVO CTI Server
# is distributed for more details.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
WEBI Interface
"""
from xivo_cti.interfaces import interfaces

import logging
import re

logger = logging.getLogger('interface_webi')

XIVO_CLI_WEBI_HEADER = 'XIVO-CLI-WEBI'

AMI_REQUESTS = [
    'core show version',
    'core show channels',
    'dialplan reload',
    'sccp reload',
    'sip reload',
    'moh reload',
    'iax2 reload',
    'module reload',
    'module reload app_queue.so',
    'module reload chan_agent.so',
    'module reload app_meetme.so',
    'features reload',
    'voicemail reload'
    ]

UPDATE_REQUESTS = [
    'xivo[cticonfig,update]',

    'xivo[userlist,update]',
    'xivo[devicelist,update]',
    'xivo[linelist,update]',
    'xivo[phonelist,update]',

    'xivo[trunklist,update]',
    'xivo[agentlist,update]',
    'xivo[queuelist,update]',
    'xivo[grouplist,update]',
    'xivo[meetmelist,update]',
    'xivo[voicemaillist,update]',
    'xivo[incalllist,update]',
    'xivo[phonebooklist,update]'
    ]


class WEBI(interfaces.Interfaces):

    kind = 'WEBI'
    sep = '\\n'  # this instead of \n is done in order to match wrong WEBI implementation

    def __init__(self, ctiserver):
        interfaces.Interfaces.__init__(self, ctiserver)

    def connected(self, connid):
        interfaces.Interfaces.connected(self, connid)

    def disconnected(self, msg):
        interfaces.Interfaces.disconnected(self, msg)

    def set_ipbxid(self, ipbxid):
        self.ipbxid = ipbxid

    def manage_connection(self, msg):
        multimsg = msg.replace('\r', '').split(self.sep)
        clireply = []
        closemenow = True

        for iusefulmsg in multimsg:
            usefulmsg = iusefulmsg.strip()
            if len(usefulmsg) == 0:
                break
            try:
                if usefulmsg == 'xivo[daemon,reload]':
                    self._ctiserver.askedtoquit = True
                elif usefulmsg in UPDATE_REQUESTS:
                    self._ctiserver.update_userlist[self.ipbxid].append(usefulmsg)
                elif usefulmsg in AMI_REQUESTS:
                    self._ctiserver.myami.get(self.ipbxid).delayed_action(usefulmsg, self)
                    closemenow = False
                else:
                    recomp = re.compile('sip show peer .* load')
                    if re.match(recomp, usefulmsg):
                        self._ctiserver.myami.get(self.ipbxid).delayed_action(usefulmsg, self)
                        closemenow = False
                    else:
                        logger.warning('WEBI did an unexpected request %s', usefulmsg)
            except Exception:
                logger.exception('WEBI connection [%s] : KO when defining for %s',
                                 usefulmsg, self.requester)

        freply = [{'message': clireply,
                   'closemenow': closemenow}]
        return freply

    def reply(self, replylines):
        try:
            for replyline in replylines:
                self.connid.sendall('%s\n' % replyline)
        except Exception:
            logger.exception('WEBI connection [%s] : KO when sending to %s',
                             replylines, self.requester)

    def makereply_close(self, actionid, status, reply=[]):
        if self.connid:
            try:
                self.connid.sendall('%s:ID <%s>\n' % (XIVO_CLI_WEBI_HEADER, self.ipbxid))
                for r in reply:
                    self.connid.sendall('%s\n' % r)
                self.connid.sendall('%s:%s\n' % (XIVO_CLI_WEBI_HEADER, status))
            except Exception:
                logger.warning('failed a WEBI reply %s for %s (disconnected)', status, actionid)
            if self.connid in self._ctiserver.fdlist_established:
                del self._ctiserver.fdlist_established[self.connid]
            self.connid.close()
        else:
            logger.warning('failed a WEBI reply %s for %s (connid None)', status, actionid)
