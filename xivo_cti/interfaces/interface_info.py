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
from xivo_cti.ioc.context import context

logger = logging.getLogger('interface_info')

infohelptext = ['',
                'help                     : this help',
                '-- general purpose commands --',
                'show_infos               : gives a few informations about the server (version, uptime)',
                '-- informations about misc lists --',
                'showlist [listname [id]] : show all lists or the specified list'
                '-- selective lists --',
                'show_logged              : only the logged users',
                'show_logged_ip           : the human-readable IPs of logged users',
                '-- for debugging purposes --',
                'loglevel set <level>         : changes the syslog output level',
                'show_varsizes <astid>        : gives the number of items of some variables',
                'show_var <astid> <varname>   : outputs the contents of one such variable',
                'dumpami enable               : enables the line-by-line display of all AMI events',
                'dumpami enable Dial,Hangup   : enables the line-by-line display of these 2 AMI events',
                'dumpami disable              : disables the line-by-line display of all AMI events',
                'dumpami disable Dial,Hangup  : enables the line-by-line display of all but these 2 AMI events',
                'dumpami                      : shows the current settings of this line-by-line display',
                '-- slightly advanced features --',
                'disc <ip> <port>             : closes the socket linked to <ip>:<port> if present',
                'ami <astid> <command> <args> : executes the CTI-defined AMI function on <astid>',
                'reverse <dirname> <number>   : lookup the number in the given directory',
                '']


class INFO(interfaces.Interfaces):

    kind = 'INFO'
    sep = '\n'

    def __init__(self, ctiserver):
        interfaces.Interfaces.__init__(self, ctiserver)
        self.dumpami_enable = []
        self.dumpami_disable = []
        self.innerdata = context.get('innerdata')
        self._ami_18 = context.get('ami_18')

    def connected(self, connid):
        interfaces.Interfaces.connected(self, connid)

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

                elif usefulmsg == 'show_infos':
                    time_uptime = int(time.time() - time.mktime(self._ctiserver.time_start))
                    reply = 'infos=' \
                            'commandset=%s;' \
                            'uptime=%d s' \
                            % (self._ctiserver.servername,
                               time_uptime)
                    clireply.append(reply)
                    # clireply.append('server capabilities = %s' % (','.join()))

                elif usefulmsg.startswith('dumpami'):
                    command_args = usefulmsg.split()
                    if len(command_args) > 1:
                        action = command_args[1]
                        if action == 'enable':
                            if len(command_args) > 2:
                                self.dumpami_enable = command_args[2].split(',')
                                self.dumpami_disable = []
                            else:
                                self.dumpami_enable = ['all']
                                self.dumpami_disable = []
                        elif action == 'disable':
                            if len(command_args) > 2:
                                self.dumpami_enable = ['all']
                                self.dumpami_disable = command_args[2].split(',')
                            else:
                                self.dumpami_enable = []
                                self.dumpami_disable = []
                        else:
                            clireply.append('dumpami status : enable (%s) disable (%s)'
                                            % (','.join(self.dumpami_enable),
                                               ','.join(self.dumpami_disable)))
                    else:
                        clireply.append('dumpami status : enable (%s) disable (%s)'
                                        % (','.join(self.dumpami_enable),
                                           ','.join(self.dumpami_disable)))

                elif usefulmsg.startswith('loglevel '):
                    command_args = usefulmsg.split()
                    if len(command_args) > 2:
                        action = command_args[1]
                        levelname = command_args[2]
                        levels = {
                            'debug': logging.DEBUG,
                            'info': logging.INFO,
                            'warning': logging.WARNING,
                            'error': logging.ERROR
                        }
                        if action == 'set':
                            if levelname in levels:
                                newlevel = levels[levelname]
                                logger.setLevel(logging.INFO)
                                logger.info('=== setting loglevel to %s (%s) ===', levelname, newlevel)
                                logger.setLevel(newlevel)
                                logging.getLogger('xivocti').setLevel(newlevel)
                                logging.getLogger('xivo_ami').setLevel(newlevel)
                                clireply.append('loglevel set to %s (%s)' % (levelname, newlevel))
                            else:
                                clireply.append('unknown level name <%s> to set' % levelname)
                        elif action == 'get':
                            pass
                        else:
                            clireply.append('unknown action <%s> for loglevel : try set or get' % action)

                elif usefulmsg.startswith('showlist'):
                    args = usefulmsg.split()
                    safe = self._ctiserver.safe
                    clireply.append('ipbxid : %s' % self._ctiserver.myipbxid)
                    for k, v in safe.xod_config.iteritems():
                        if len(args) > 1 and not args[1] in k:
                            continue
                        clireply.append('    %s' % k)
                        for kk, vv in v.keeplist.iteritems():
                            if len(args) > 2 and not kk in args[2]:
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

                elif usefulmsg.startswith('show_var '):
                    command_args = usefulmsg.split()
                    if len(command_args) > 2:
                        astid = command_args[1]
                        varname = command_args[2]
                        if hasattr(self._ami_18, varname):
                            tvar = getattr(self._ami_18, varname)
                            if astid in tvar:
                                clireply.append('%s on %s' % (varname, astid))
                                for ag, agp in tvar[astid].iteritems():
                                    clireply.append('%s %s' % (ag, agp))
                            else:
                                clireply.append('no such astid %s' % astid)
                        else:
                            clireply.append('no such variable %s' % varname)
                    else:
                        clireply.append('first argument : astid value')
                        clireply.append('second argument : one of %s' % self._ami_18.astid_vars)

                elif usefulmsg.startswith('show_varsizes '):
                    command_args = usefulmsg.split()
                    if len(command_args) > 1:
                        astid = command_args[1]
                        for varname in self._ami_18.astid_vars:
                            if hasattr(self._ami_18, varname):
                                tvar = getattr(self._ami_18, varname)
                                if astid in tvar:
                                    clireply.append('%s on %s: %d' % (varname, astid, len(tvar[astid])))
                                else:
                                    clireply.append('no such astid %s' % astid)
                            else:
                                clireply.append('no such variable %s' % varname)
                    else:
                        clireply.append('argument : astid value')

                elif usefulmsg == 'fdlist':
                    for k, v in self._ctiserver.fdlist_listen_cti.iteritems():
                        clireply.append('  listen TCP : %s %s' % (k, v))
                    for k, v in self._ctiserver.fdlist_established.iteritems():
                        clireply.append('  conn   TCP : %s %s' % (k, v))
                    clireply.append('  full : %s' % self._ctiserver.fdlist_full)

                elif usefulmsg.startswith('disc '):
                    command_args = usefulmsg.split()
                    if len(command_args) > 2:
                        ipdef = tuple([command_args[1], int(command_args[2])])
                        socktoremove = None
                        for sockid in self._ctiserver.fdlist_established.keys():
                            if ipdef == sockid.getpeername():
                                socktoremove = sockid
                        if socktoremove:
                            clireply.append('disconnecting %s (%s)'
                                           % (socktoremove.getpeername(),
                                              self._ctiserver.fdlist_established[socktoremove]))
                            socktoremove.close()
                            del self._ctiserver.fdlist_established[socktoremove]
                        else:
                            clireply.append('nobody disconnected')

                elif usefulmsg == 'show_ami':
                    for astid, ami in self._ctiserver.amilist.ami.iteritems():
                        clireply.append('commands : %s : %s' % (astid, ami))

                elif usefulmsg.startswith('ami inits '):
                    g = usefulmsg[10:]
                    self._ctiserver.interface_ami.initrequest(g)

                elif usefulmsg.startswith('ami '):
                    amicmd = usefulmsg.split()[1:]
                    if amicmd:
                        clireply.append('ami request %s' % amicmd)
                        if len(amicmd) > 1:
                            astid = amicmd[0]
                            cmd = amicmd[1]
                            cmdargs = amicmd[2:]
                            self._ctiserver.amilist.execute(astid, cmd, *cmdargs)

                elif usefulmsg.startswith('reload '):
                    listname = usefulmsg[7:]
                    self.innerdata.update_config_list(listname)

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
