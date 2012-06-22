# vim: set fileencoding=utf-8 :
# XiVO CTI Server
__copyright__ = 'Copyright (C) 2007-2012  Avencall'

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Avencall. See the LICENSE file at top of the source tree
# or delivered in the installable package in which XiVO CTI Server is
# distributed for more details.
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

from xivo_cti import cti_config
from xivo_cti.interfaces import interfaces
from xivo_cti.services.meetme.service_manager import manager as meetme_manager

import logging

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
    'voicemail reload',
    'module reload chan_sccp.so',
    'sccp show version',
    'sccp show devices',
    'sccp show config',
    'sccp update config',
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


class BadWebiCommandException(Exception):
    pass


class WEBI(interfaces.Interfaces):
    kind = 'WEBI'

    def __init__(self, ctiserver):
        interfaces.Interfaces.__init__(self, ctiserver)
        self._config = cti_config.Config.get_instance()

    def connected(self, connid):
        interfaces.Interfaces.connected(self, connid)

    def disconnected(self, cause):
        interfaces.Interfaces.disconnected(self, cause)

    def _parse_webi_command(self, raw_msg):
        if len(raw_msg) == 0 or not ':' in raw_msg:
            logger.warning('WEBI did an unexpected request %s', raw_msg)
            raise BadWebiCommandException()

        raw_msg = raw_msg.strip()
        type = raw_msg.split(':')[0]
        msg = raw_msg.split(':')[1]

        if type not in ['sync', 'async']:
            logger.warning('WEBI did an unexpected type %s', type)
            raise BadWebiCommandException()
        elif len(msg) == 0:
            logger.warning('WEBI send empty msg')
            raise BadWebiCommandException()

        if type == 'sync':
            logger.info('Synchronous WEBI command received: %s', msg)
        else:
            logger.info('Asynchronous WEBI command received: %s', msg)

        return (type, msg)

    def _send_ami_request(self, type, msg):
        if type == 'async':
            self._ctiserver.myami.delayed_action(msg)
            return True
        else:
            self._ctiserver.myami.delayed_action(msg, self)
            return False

    def manage_connection(self, raw_msg):
        clireply = []
        closemenow = True

        live_reload_conf = self._config.getconfig('main')['live_reload_conf']

        if not live_reload_conf:
            logger.info('WEBI command received (%s) but live reload configuration has been disabled', raw_msg)
            return [{'message': clireply,
                     'closemenow': closemenow}]

        try:
            type, msg = self._parse_webi_command(raw_msg)
        except BadWebiCommandException:
            return [{'message': clireply,
                     'closemenow': closemenow}]

        if msg == 'xivo[daemon,reload]':
            self._ctiserver.askedtoquit = True
        elif msg == 'xivo[queuemember,update]':
            self.queuemember_service_manager.update_config()
        elif msg in UPDATE_REQUESTS:
            self._ctiserver.update_userlist.append(msg)
            if msg == 'xivo[meetmelist,update]':
                meetme_manager.initialize()
        elif msg in AMI_REQUESTS:
            closemenow = self._send_ami_request(type, msg)
        elif msg.startswith('sip show peer '):
            closemenow = self._send_ami_request(type, msg)
        else:
            logger.warning('WEBI did an unexpected request %s', msg)

        return [{'message': clireply,
                 'closemenow': closemenow}]

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
                self.connid.sendall('%s\n' % (XIVO_CLI_WEBI_HEADER))
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
