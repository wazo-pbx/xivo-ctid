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
Info Interface
"""

import logging
import time

from xivo_cti.interfaces import Interfaces

logger = logging.getLogger('interface_info')

infohelptext = ['',
                'help                     : this help',
                '-- general purpose commands --',
                'show_infos               : gives a few informations about the server (version, uptime)',
                '-- informations about misc lists --',
                'showlist [listname [id]] : show all lists or the specified list'
                'show_users               : the users list',
                'show_phones, show_trunks : phones and trunks lists',
                'show_queues, show_groups,',
                'show_agents              : call-center related lists',
                'show_incalls             : did lists',
                'show_outcalls            : out calls',
                'show_meetme              : conference rooms',
                'show_voicemail           : voicemails',
                'show_phonebook           : phonebook contents',
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
                'kick <user>                  : disconnects the user <user>',
                'disc <ip> <port>             : closes the socket linked to <ip>:<port> if present',
                'ami <astid> <command> <args> : executes the CTI-defined AMI function on <astid>',
                'reverse <dirname> <number>   : lookup the number in the given directory',
                '']

class INFO(Interfaces):
    kind = 'INFO'
    sep = '\n'
    def __init__(self, ctiserver):
        Interfaces.__init__(self, ctiserver)
        self.dumpami_enable = []
        self.dumpami_disable = []
        return

    def connected(self, connid):
        Interfaces.connected(self, connid)

    def disconnected(self, msg):
        self.connid.sendall('-- disconnected message from server at %s : %s\n' % (time.asctime(), msg))
        Interfaces.disconnected(self, msg)
        return

    def set_ipbxid(self, ipbxid):
        self.ipbxid = ipbxid
        self.innerdata = self._ctiserver.safe.get(self.ipbxid)

    def manage_connection(self, msg):
        """
        Handles INFO connections (basic administration console,
        primarily aimed at displaying informations first).
        """
        multimsg = msg.replace('\r', '').split(self.sep)
        clireply = []

        for iusefulmsg in multimsg:
            usefulmsg = iusefulmsg.strip()
            if len(usefulmsg) == 0:
                break
            try:
                retstr = 'OK'
                show_command_list = ['show_phones', 'show_trunks',
                                     'show_queues', 'show_groups', 'show_agents',
                                     'show_incalls', 'show_outcalls',
                                     'show_phonebook',
                                     'show_meetme', 'show_voicemail']
                if usefulmsg == 'help':
                    clireply.extend(infohelptext)

                elif usefulmsg == 'show_xivos':
                    clireply.append('%s' % ','.join(self._ctiserver.safe.keys()))

                elif usefulmsg == 'show_infos':
                    time_uptime = int(time.time() - time.mktime(self._ctiserver.time_start))
                    reply = 'infos=' \
                            'xivo_version=%s;' \
                            'server_version=%s;' \
                            'commandset=%s;' \
                            'uptime=%d s' \
                            % (self._ctiserver.xivoversion,
                               self._ctiserver.revision,
                               self._ctiserver.xdname,
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

                elif usefulmsg.startswith('devcheckevents'):
                    for k in sorted(xivo_ami.evfunction_to_method_name.keys()):
                        v = xivo_ami.evfunction_to_method_name.get(k)
                        if not hasattr(self._ctiserver.commandclass, v):
                            clireply.append('devcheckevents : unavailable %s' % k)

                elif usefulmsg.startswith('loglevel '):
                    command_args = usefulmsg.split()
                    if len(command_args) > 2:
                        action = command_args[1]
                        levelname = command_args[2]
                        levels = { 'debug' : logging.DEBUG,
                                   'info' : logging.INFO,
                                   'warning' : logging.WARNING,
                                   'error' : logging.ERROR}
                        if action == 'set':
                            if levelname in levels:
                                newlevel = levels[levelname]
                                logger.setLevel(logging.INFO)
                                logger.info('=== setting loglevel to %s (%s) ===', levelname, newlevel)
                                logger.setLevel(newlevel)
                                logging.getLogger('xivocti').setLevel(newlevel)
                                logging.getLogger('xivo_ami').setLevel(newlevel)
                                logging.getLogger('urllist').setLevel(newlevel)
                                clireply.append('loglevel set to %s (%s)' % (levelname, newlevel))
                            else:
                                clireply.append('unknown level name <%s> to set' % levelname)
                        elif action == 'get':
                            pass
                        else:
                            clireply.append('unknown action <%s> for loglevel : try set or get' % action)

                elif usefulmsg.startswith('showlist'):
                    args = usefulmsg.split()
                    for ipbxid, z in self._ctiserver.safe.iteritems():
                        clireply.append('ipbxid : %s' % ipbxid)
                        for k, v in z.xod_config.iteritems():
                            if len(args) > 1 and not args[1] in k:
                                continue
                            clireply.append('    %s' % k)
                            for kk, vv in v.keeplist.iteritems():
                                if len(args) > 2 and not kk in args[2]:
                                    continue
                                listname, id = k, kk
                                clireply.append('        %s %s' %
                                                (listname, id))
                                clireply.append('        config: \n%s' % vv)
                                try:
                                    clireply.append('        status:\n%s' %
                                                    z.xod_status[listname][id])
                                except KeyError:
                                    clireply.append('        status: None')
##                    for user, info in self.ctid.safe.get(ipbxid).xod_config..users().iteritems():
##                        try:
##                            clireply.append('%s %s' % (user.encode('latin1'), info))
##                        except Exception:
##                            logger.exception('INFO %s', usefulmsg)

                elif usefulmsg in show_command_list:
                    itemname = usefulmsg[5:]
                    for astid, itm in self._ctiserver.commandclass.getdetails(itemname).iteritems():
                        try:
                            clireply.append('%s for %s' % (itemname, astid))
                            for id, idv in itm.keeplist.iteritems():
                                clireply.append('%s %s' % (id, idv))
                        except Exception:
                            logger.exception('INFO %s', usefulmsg)

                elif usefulmsg.startswith('show_var '):
                    command_args = usefulmsg.split()
                    if len(command_args) > 2:
                        astid = command_args[1]
                        varname = command_args[2]
                        if hasattr(self._ctiserver.commandclass, varname):
                            tvar = getattr(self._ctiserver.commandclass, varname)
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
                        clireply.append('second argument : one of %s' % self._ctiserver.commandclass.astid_vars)

                elif usefulmsg.startswith('show_varsizes '):
                    command_args = usefulmsg.split()
                    if len(command_args) > 1:
                        astid = command_args[1]
                        for varname in self._ctiserver.commandclass.astid_vars:
                            if hasattr(self._ctiserver.commandclass, varname):
                                tvar = getattr(self._ctiserver.commandclass, varname)
                                if astid in tvar:
                                    clireply.append('%s on %s: %d' % (varname, astid, len(tvar[astid])))
                                else:
                                    clireply.append('no such astid %s' % astid)
                            else:
                                clireply.append('no such variable %s' % varname)
                    else:
                        clireply.append('argument : astid value')

                elif usefulmsg == 'show_logged_ip':
                    for user, info in self._ctiserver.commandclass.connected_users().iteritems():
                        if 'connection' in info['login']:
                            try:
                                [ipaddr, ipport] = info['login']['connection'].getpeername()
                            except Exception:
                                logger.exception('INFO %s', usefulmsg)
                                [ipaddr, ipport] = ['err_addr', 'err_port']
                            clireply.append('user %s : ip:port = %s:%s'
                                            % (user.encode('latin1'), ipaddr, ipport))

                elif usefulmsg == 'show_logged':
                    for user, info in self._ctiserver.commandclass.connected_users().iteritems():
                        try:
                            clireply.append('%s %s' % (user.encode('latin1'), info))
                        except Exception:
                            logger.exception('INFO %s', usefulmsg)

                elif usefulmsg.startswith('sheet '):
                    k = usefulmsg.split(' ')
                    self.innerdata.sheetsend(k[1], k[2])
                    clireply.append('thank you !')

                elif usefulmsg == 'fdlist':
                    for k, v in self._ctiserver.fdlist_listen_cti.iteritems():
                        clireply.append('  listen TCP : %s %s' % (k, v))
                    for k, v in self._ctiserver.fdlist_udp_cti.iteritems():
                        clireply.append('  listen UDP : %s %s' % (k, v))
                    for k, v in self._ctiserver.fdlist_established.iteritems():
                        clireply.append('  conn   TCP : %s %s' % (k, v))
                    clireply.append('  full : %s' % self._ctiserver.fdlist_full)

                elif usefulmsg.startswith('reverse '):
                    command_args = usefulmsg.split()
                    if len(command_args) > 2:
                        context = command_args[1]
                        numbers = command_args[2:]
                        for number in numbers:
                            reverses = self._ctiserver.safe[self._ctiserver.myipbxid].findreverse(context, '*', number)
                            for number, rep in reverses.iteritems():
                                if isinstance(rep, unicode):
                                    clireply.append('%s %s' % (number, rep.encode('utf8')))
                                else:
                                    clireply.append('%s %s' % (number, rep))

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
                    self._ctiserver.myami[self.ipbxid].initrequest(g)

                elif usefulmsg.startswith('ami '):
                    amicmd = usefulmsg.split()[1:]
                    if amicmd:
                        clireply.append('ami request %s' % amicmd)
                        if len(amicmd) > 1:
                            astid = amicmd[0]
                            cmd = amicmd[1]
                            cmdargs = amicmd[2:]
                            self._ctiserver.amilist.execute(astid, cmd, *cmdargs)

                elif usefulmsg.startswith('webs reload '):
                    listname = usefulmsg[12:]
                    self.innerdata.update_config_list(listname)

                elif usefulmsg == 'currentstatus':
                    clireply.extend(self.innerdata.currentstatus())

                elif usefulmsg.startswith('kick '):
                    command_args = usefulmsg.split()
                    try:
                        if len(command_args) > 1:
                            kickuser = command_args[1]
                            if kickuser in self._ctiserver.commandclass.connected_users():
                                uinfo = self._ctiserver.commandclass.connected_users()[kickuser]
                                if 'login' in uinfo and 'connection' in uinfo.get('login'):
                                    cid = uinfo.get('login')['connection']
                                    if cid in self._ctiserver.fdlist_established:
                                        del self._ctiserver.fdlist_established[cid]
                                        cid.close()
                                        self._ctiserver.commandclass.manage_logout(uinfo, 'admin')
                                        del self._ctiserver.userinfo_by_requester[cid]
                                        clireply.append('kicked %s' % kickuser)
                                    else:
                                        clireply.append('did not kick %s (socket id not in daemon refs)'
                                                        % kickuser)
                                else:
                                    clireply.append('did not kick %s (no connection attributes for the user)'
                                                    % kickuser)
                            else:
                                clireply.append('did not kick %s (user not found)'
                                                % kickuser)
                        else:
                            clireply.append('nobody to kick')
                    except Exception:
                        logger.exception('INFO %s', usefulmsg)
                        clireply.append('(exception when trying to kick - see server log)')

                elif usefulmsg.startswith('%s:' % self._ctiserver.commandset):
                    self._ctiserver.commandclass.cliaction(self.connid, usefulmsg)

                else:
                    retstr = 'KO'

                clireply.append('XIVO-INFO:%s' % retstr)
            except Exception:
                logger.exception('INFO connection [%s] : KO when defining for %s',
                                 usefulmsg, self.requester)

        freply = [ { 'message' : clireply } ]
        return freply

    def reply(self, replylines):
        try:
            for replyline in replylines:
                self.connid.sendall('%s\n' % replyline)
        except Exception:
            logger.exception('INFO connection [%s] : KO when sending to %s',
                             replylines, self.requester)
        return
