# -*- coding: utf-8 -*-

# XiVO CTI Server
#
# Copyright (C) 2007-2012  Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Avencall. See the LICENSE file at top of the souce tree
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

import logging
import random
import string
import threading
import time
from xivo_cti import cti_fax
from xivo_cti.context import context as cti_context
from xivo_cti.statistics.queue_statistics_encoder import QueueStatisticsEncoder
from xivo_dao.celdao import UnsupportedLineProtocolException
from xivo_cti.services.agent_status import AgentStatus

logger = logging.getLogger('cti_command')

LOGINCOMMANDS = [
    'login_pass', 'login_capas'
    ]

REGCOMMANDS = [
    'logout',

    'getipbxlist',
    'keepalive',

    'history',
    'faxsend',
    'filetransfer',
    'chitchat',

    'logfromclient',
    'getqueuesstats',
    'sheet',
    'actionfiche',

    'ipbxcommand'
    ]

IPBXCOMMANDS = [
    # originate-like commands
    'dial', 'originate',
    # transfer-like commands
    'intercept', 'parking',
    'transfer', 'atxfer',
    # hangup-like commands
    'hangup',

    'sipnotify',
    'mailboxcount',
    'meetme',
    'record',
    'listen',

    'queueadd', 'queueremove',
    'queuepause', 'queueunpause',
    'queueremove_all',
    'queuepause_all', 'queueunpause_all',
    ]

XIVOVERSION_NAME = 'skaro'
ALPHANUMS = string.uppercase + string.lowercase + string.digits


class Command(object):
    def __init__(self, connection, thiscommand):
        self._config = cti_context.get('config')
        self._connection = connection
        self._ctiserver = self._connection._ctiserver
        self._commanddict = thiscommand
        self._othermessages = list()
        self._queue_statistics_manager = cti_context.get('queue_statistics_manager')
        self._queue_statistics_encoder = QueueStatisticsEncoder()

    def parse(self):
        self.command = self._commanddict.get('class')
        self.commandid = self._commanddict.get('commandid')

        self.ipbxid = self._connection.connection_details.get('ipbxid')
        self.userid = self._connection.connection_details.get('userid')
        self.innerdata = self._ctiserver.safe

        # identifiers for the requester
        self.ripbxid = self._commanddict.get('ipbxid', self.ipbxid)
        self.ruserid = self._commanddict.get('userid', self.userid)
        self.rinnerdata = self._ctiserver.safe

        # identifiers for the requested
        self.tipbxid = self._commanddict.get('tipbxid', self.ipbxid)
        self.tinnerdata = self._ctiserver.safe

        messagebase = {'class': self.command}
        if self.commandid:
            messagebase['replyid'] = self.commandid

        if self.command in REGCOMMANDS and not self._connection.connection_details.get('logged'):
            messagebase['error_string'] = 'notloggedyet'

        elif self.command in LOGINCOMMANDS or self.command in REGCOMMANDS:
            if self.ripbxid:
                # regcommands = self.rinnerdata.get_user_permissions('regcommands', self.ruserid)
                regcommands = REGCOMMANDS + LOGINCOMMANDS
                if regcommands:
                    if self.command not in regcommands:
                        logger.warning('user %s/%s : unallowed command %s',
                                       self.ripbxid, self.ruserid, self.command)
                        messagebase['warning_string'] = 'unallowed'
                else:
                    logger.warning('user %s/%s : unallowed command %s - empty regcommands',
                                   self.ripbxid, self.ruserid, self.command)
                    messagebase['warning_string'] = 'no_regcommands'

            methodname = 'regcommand_%s' % self.command
            if hasattr(self, methodname) and 'warning_string' not in messagebase:
                method_result = getattr(self, methodname)()
                if not method_result:
                    messagebase['warning_string'] = 'return_is_none'
                elif isinstance(method_result, str):
                    messagebase['error_string'] = method_result
                else:
                    messagebase.update(method_result)
            else:
                messagebase['warning_string'] = 'unimplemented'
        else:
            return []

        ackmessage = {'message': messagebase}
        if 'error_string' in messagebase:
            ackmessage['closemenow'] = True

        z = [ackmessage]
        for extramessage in self._othermessages:
            bmsg = extramessage.get('message')
            bmsg['class'] = self.command
            z.append({'dest': extramessage.get('dest'),
                      'message': bmsg})
        return z

    def regcommand_login_pass(self):
        head = 'LOGINFAIL - login_pass'
        # user authentication
        missings = []
        for argum in ['hashedpassword']:
            if argum not in self._commanddict:
                missings.append(argum)
        if missings:
            logger.warning('%s - missing args : %s', head, missings)
            return 'missing:%s' % ','.join(missings)

        this_hashed_password = self._commanddict.get('hashedpassword')
        cdetails = self._connection.connection_details

        ipbxid = cdetails.get('ipbxid')
        userid = cdetails.get('userid')
        sessionid = cdetails.get('prelogin').get('sessionid')

        if ipbxid and userid:
            ref_hashed_password = self._ctiserver.safe.user_get_hashed_password(userid, sessionid)
            if ref_hashed_password != this_hashed_password:
                logger.warning('%s - wrong hashed password', head)
                return 'login_password'
        else:
            logger.warning('%s - undefined user : probably the login_id step failed', head)
            return 'login_password'

        reply = {'capalist': [self._ctiserver._user_features_dao.get_profile(userid)]}
        return reply

    def regcommand_login_capas(self):
        head = 'LOGINFAIL - login_capas'
        missings = []
        for argum in ['state', 'capaid', 'lastconnwins', 'loginkind']:
            if argum not in self._commanddict:
                missings.append(argum)
        if missings:
            logger.warning('%s - missing args : %s', head, missings)
            return 'missing:%s' % ','.join(missings)

        # settings (in agent mode for instance)
        # userinfo['agent']['phonenum'] = phonenum
        cdetails = self._connection.connection_details

        state = self._commanddict.get('state')
        capaid = self._commanddict.get('capaid')

        iserr = self.__check_capa_connection__(capaid)
        if iserr is not None:
            logger.warning('%s - wrong capaid : %s %s', head, iserr, capaid)
            return iserr

        iserr = self.__check_user_connection__()
        if iserr is not None:
            logger.warning('%s - user connection : %s', head, iserr)
            return iserr

        self.__connect_user__(state, capaid)
        head = 'LOGIN SUCCESSFUL'
        logger.info('%s for %s', head, cdetails)

        if self.userid.startswith('cs:'):
            notifyremotelogin = threading.Timer(2, self._ctiserver.cb_timer,
                                                ({'action': 'xivoremote',
                                                  'properties': None}))
            notifyremotelogin.setName('Thread-xivo-%s' % self.userid)
            notifyremotelogin.start()

        profileclient = self.innerdata.xod_config['users'].keeplist[self.userid].get('profileclient')
        profilespecs = self._config.getconfig('profiles').get(profileclient)

        capastruct = {}
        summarycapas = {}
        if profilespecs:
            for capakind in ['regcommands', 'ipbxcommands',
                             'services', 'preferences',
                             'userstatus', 'phonestatus']:
                if profilespecs.get(capakind):
                    tt = profilespecs.get(capakind)
                    cfg_capakind = self._config.getconfig(capakind)
                    if cfg_capakind:
                        details = cfg_capakind.get(tt)
                    else:
                        details = {}
                    capastruct[capakind] = details
                    if details:
                        summarycapas[capakind] = tt
                else:
                    capastruct[capakind] = {}

        reply = {'ipbxid': self.ipbxid,
                 'userid': self.userid,
                 'appliname': profilespecs.get('name'),
                 'capaxlets': profilespecs.get('xlets'),
                 'capas': capastruct,
                 'presence': 'available'}

        self._connection.connection_details['logged'] = True
        self._connection.logintimer.cancel()
        return reply

    def __check_user_connection__(self):
        return

    def __check_capa_connection__(self, capaid):
        cdetails = self._connection.connection_details
        ipbxid = cdetails.get('ipbxid')
        userid = cdetails.get('userid')
        if capaid not in self._config.getconfig('profiles').keys():
            return 'unknownprofile'
        if capaid != self._ctiserver.safe.xod_config['users'].keeplist[userid]['profileclient']:
            return 'wrongprofile'
        # XXX : too much users ?

    def __connect_user__(self, availstate, c):
        cdetails = self._connection.connection_details
        ipbxid = cdetails.get('ipbxid')
        userid = cdetails.get('userid')
        self._ctiserver.safe.xod_status['users'][userid]['connection'] = 'yes'
        self._ctiserver._user_service_manager.set_presence(userid, availstate)

    # end of login/logout related commands

    def regcommand_chitchat(self):
        reply = {}
        chitchattext = self._commanddict.get('text')
        self._othermessages.append({'dest': self._commanddict.get('to'),
                                   'message': {'to': self._commanddict.get('to'),
                                               'from': '%s/%s' % (self.ripbxid, self.ruserid),
                                                'text': chitchattext}})
        return reply

    def regcommand_actionfiche(self):
        reply = {}
        infos = self._commanddict.get('infos')
        uri = self._config.getconfig('ipbx').get('db_uri')
        self.rinnerdata.fill_user_ctilog(uri,
                                         self.ruserid,
                                         'cticommand:actionfiche',
                                         infos.get('buttonname'))
        logger.info('Received from client : %s' % infos.get('variables'))
        return reply

    def regcommand_history(self):
        phone = self._get_phone_from_user_id(self.ruserid, self.rinnerdata)
        if phone is None:
            reply = self._format_history_reply(None)
        else:
            history = self._get_history_for_phone(phone)
            reply = self._format_history_reply(history)
        return reply

    def _get_phone_from_user_id(self, user_id, innerdata):
        for phone in innerdata.xod_config['phones'].keeplist.itervalues():
            if str(phone['iduserfeatures']) == user_id:
                return phone
        return None

    def _get_history_for_phone(self, phone):
        mode = int(self._commanddict['mode'])
        limit = int(self._commanddict['size'])
        try:
            if mode == 0:
                return self._get_outgoing_history_for_phone(phone, limit)
            elif mode == 1:
                return self._get_answered_history_for_phone(phone, limit)
            elif mode == 2:
                return self._get_missed_history_for_phone(phone, limit)
        except UnsupportedLineProtocolException:
            logger.warning('Could not get history for phone: %s', phone['name'])
        return None

    def _get_outgoing_history_for_phone(self, phone, limit):
        call_history_mgr = self.rinnerdata.call_history_mgr
        result = []
        for sent_call in call_history_mgr.outgoing_calls_for_phone(phone, limit):
            result.append({'calldate': sent_call.date.isoformat(),
                           'duration': sent_call.duration,
                           # XXX this is not fullname, this is just an extension number like in 1.1
                           'fullname': sent_call.extension})
        return result

    def _get_answered_history_for_phone(self, phone, limit):
        call_history_mgr = self.rinnerdata.call_history_mgr
        result = []
        for received_call in call_history_mgr.answered_calls_for_phone(phone, limit):
            result.append({'calldate': received_call.date.isoformat(),
                           'duration': received_call.duration,
                           'fullname': received_call.caller_name})
        return result

    def _get_missed_history_for_phone(self, phone, limit):
        call_history_mgr = self.rinnerdata.call_history_mgr
        result = []
        for received_call in call_history_mgr.missed_calls_for_phone(phone, limit):
            result.append({'calldate': received_call.date.isoformat(),
                           'duration': received_call.duration,
                           'fullname': received_call.caller_name})
        return result

    def _format_history_reply(self, history):
        if history is None:
            return {}
        else:
            mode = int(self._commanddict['mode'])
            return {'mode': mode, 'history': history}

    def regcommand_logfromclient(self):
        logger.warning('logfromclient from user %s (level %s) : %s : %s',
                         self.ruserid,
                         self._commanddict.get('level'),
                         self._commanddict.get('classmethod'),
                         self._commanddict.get('message'))

    def regcommand_getqueuesstats(self):
        if 'on' not in self._commanddict:
            return {}
        statistic_results = {}
        for queue_id, params in self._commanddict['on'].iteritems():
            queue_name = self.innerdata.xod_config['queues'].keeplist[queue_id]['name']
            statistic_results[queue_id] = self._queue_statistics_manager.get_statistics(queue_name,
                                                                                        int(params['xqos']),
                                                                                        int(params['window']))
        return self._queue_statistics_encoder.encode(statistic_results)

    def regcommand_filetransfer(self):
        reply = {}
        function = self._commanddict.get('command')
        socketref = self._commanddict.get('socketref')
        fileid = self._commanddict.get('fileid')
        if fileid:
            self.innerdata.faxes[fileid].setsocketref(socketref)
            self.innerdata.faxes[fileid].setfileparameters(self._commanddict.get('file_size'))
            if function == 'get_announce':
                self._ctiserver.set_transfer_socket(self.innerdata.faxes[fileid], 's2c')
            elif function == 'put_announce':
                self._ctiserver.set_transfer_socket(self.innerdata.faxes[fileid], 'c2s')
        else:
            logger.warning('empty fileid given %s', self._commanddict)
        return reply

    def regcommand_faxsend(self):
        fileid = ''.join(random.sample(ALPHANUMS, 10))
        reply = {'fileid': fileid}
        self.innerdata.faxes[fileid] = cti_fax.Fax(self.innerdata, fileid)
        contexts = self.innerdata.xod_config['users'].get_contexts(self.userid)
        if contexts:
            self.innerdata.faxes[fileid].setfaxparameters(self.ruserid,
                                                          contexts[0],
                                                          self._commanddict.get('destination'),
                                                          self._commanddict.get('hide'))
            self.innerdata.faxes[fileid].setrequester(self._connection)
        return reply

    def regcommand_getipbxlist(self):
        return {'ipbxlist': ['xivo']}

    def regcommand_ipbxcommand(self):
        reply = {}
        self.ipbxcommand = self._commanddict.get('command')
        if not self.ipbxcommand:
            return reply
        reply['command'] = self.ipbxcommand
        if self.ipbxcommand not in IPBXCOMMANDS:
            return None
        profileclient = self.rinnerdata.xod_config['users'].keeplist[self.ruserid].get('profileclient')
        profilespecs = self._config.getconfig('profiles').get(profileclient)
        ipbxcommands_id = profilespecs.get('ipbxcommands')
        # ipbxcommands = self._config.getconfig('ipbxcommands').get(ipbxcommands_id)
        ipbxcommands = IPBXCOMMANDS
        if self.ipbxcommand not in ipbxcommands:
            logger.warning('profile %s : unallowed ipbxcommand %s (intermediate %s)',
                           profileclient, self.ipbxcommand, ipbxcommands_id)
            return reply

        methodname = 'ipbxcommand_%s' % self.ipbxcommand

        # check whether ipbxcommand is in the users's profile capabilities
        zs = []
        if hasattr(self, methodname):
                zs = getattr(self, methodname)()

        # if some actions have been requested ...
        if self.commandid:  # pass the commandid on the actionid # 'user action - forwarded'
            baseactionid = 'uaf:%s' % self.commandid
        else:  # 'user action - auto'
            baseactionid = 'uaa:%s' % ''.join(random.sample(ALPHANUMS, 10))
        ipbxreply = 'noaction'
        idz = 0
        for z in zs:
            if 'amicommand' in z:
                params = {'mode': 'useraction',
                          'request': {'requester': self._connection,
                                      'ipbxcommand': self.ipbxcommand,
                                      'commandid': self.commandid},
                          'amicommand': z.get('amicommand'),
                          'amiargs': z.get('amiargs')}
                actionid = '%s-%03d' % (baseactionid, idz)
                ipbxreply = self._ctiserver.myami.execute_and_track(actionid, params)
            else:
                ipbxreply = z.get('error')
            idz += 1

        reply['ipbxreply'] = ipbxreply
        return reply

    # "any number" :
    # - an explicit number
    # - a phone line given by line:xivo/45
    # - a user given by user:xivo/45 : attempted line will be the first one

    # dial : the requester dials "any number" (originate with source = me)
    # originate : the source will call destination

    # intercept
    # transfer
    # atxfer
    # park

    # hangup : any channel is hanged up

    # for transfers, hangups, ...

    def ipbxcommand_dial(self):
        self._commanddict['source'] = 'user:%s/%s' % (self.ripbxid, self.ruserid)
        reply = self.ipbxcommand_originate()
        return reply

    def parseid(self, item):
        id_as_obj = {}
        try:
            [typev, who] = item.split(':', 1)
            [ipbxid, idv] = who.split('/', 1)
            id_as_obj = {'type': typev,
                         'ipbxid': ipbxid,
                         'id': idv}
        except Exception:
            pass
        return id_as_obj

    # origination
    def ipbxcommand_originate(self):
        src = self.parseid(self._commanddict.get('source'))
        if not src:
            return [{'error': 'source'}]
        dst = self.parseid(self._commanddict.get('destination'))
        if not dst:
            return [{'error': 'destination'}]

        innerdata = self._ctiserver.safe

        orig_protocol = None
        orig_name = None
        orig_number = None
        orig_context = None
        phoneidstruct_src = {}
        phoneidstruct_dst = {}

        if src.get('type') == 'user':
            if src.get('id') in innerdata.xod_config.get('users').keeplist:
                for k, v in innerdata.xod_config.get('phones').keeplist.iteritems():
                    if src.get('id') == str(v.get('iduserfeatures')):
                        phoneidstruct_src = innerdata.xod_config.get('phones').keeplist.get(k)
                        break
                # if not phoneidstruct_src: lookup over agents ?
        elif src.get('type') == 'phone':
            if src.get('id') in innerdata.xod_config.get('phones').keeplist:
                phoneidstruct_src = innerdata.xod_config.get('phones').keeplist.get(src.get('id'))
        elif src.get('type') == 'exten':
            orig_context = 'mamaop'  # XXX how should we define or guess the proper context here ?
            orig_protocol = 'local'
            orig_name = '%s@%s' % (src.get('id'), orig_context)  # this is the number actually dialed, in local channel mode
            orig_number = src.get('id')  # this is the number that will be displayed as ~ callerid
            orig_identity = ''  # how would we know the identity there ?

        if phoneidstruct_src:
            orig_protocol = phoneidstruct_src.get('protocol')
            orig_name = phoneidstruct_src.get('name')
            orig_number = phoneidstruct_src.get('number')
            orig_identity = phoneidstruct_src.get('useridentity')
            orig_context = phoneidstruct_src.get('context')

        extentodial = None
        dst_identity = None

        if dst.get('type') == 'user':
            if dst.get('id') in innerdata.xod_config.get('users').keeplist:
                for k, v in innerdata.xod_config.get('phones').keeplist.iteritems():
                    if dst.get('id') == str(v.get('iduserfeatures')):
                        phoneidstruct_dst = innerdata.xod_config.get('phones').keeplist.get(k)
                        break
                # if not phoneidstruct_dst: lookup over agents ?
        elif dst.get('type') == 'phone':
            if dst.get('id') in innerdata.xod_config.get('phones').keeplist:
                phoneidstruct_dst = innerdata.xod_config.get('phones').keeplist.get(dst.get('id'))
        elif dst.get('type') == 'voicemail':
            try:
                vmusermsg = innerdata.extenfeatures['extenfeatures']['vmusermsg']
                vm = innerdata.xod_config['voicemails'].keeplist[dst['id']]
                if not vmusermsg['commented']:
                    extentodial = vmusermsg['exten']
                    dst_context = vm['context']
                    dst_identity = 'Voicemail'
                else:
                    extentodial = None
            except KeyError:
                logger.exception('Missing info to call this voicemail')
                extentodial = None
            # XXX especially for the 'dial' command, actually
            # XXX display password on phone in order for the user to know what to type
        elif dst.get('type') == 'meetme':
            if dst.get('id') in innerdata.xod_config.get('meetmes').keeplist:
                meetmestruct = innerdata.xod_config.get('meetmes').keeplist.get(dst.get('id'))
                extentodial = meetmestruct.get('confno')
                dst_identity = 'meetme %s' % meetmestruct.get('name')
                dst_context = meetmestruct.get('context')
            else:
                extentodial = None
        elif dst.get('type') == 'exten':
            extentodial = dst.get('id')
            dst_identity = extentodial
            dst_context = orig_context

        if phoneidstruct_dst:
            extentodial = phoneidstruct_dst.get('number')
            dst_identity = phoneidstruct_dst.get('useridentity')
            dst_context = phoneidstruct_dst.get('context')

        rep = {}
        if orig_protocol and orig_name and orig_number and extentodial:
            rep = {'amicommand': 'originate',
                   'amiargs': (orig_protocol,
                               orig_name,
                               orig_number,
                               orig_identity,
                               extentodial,
                               dst_identity,
                               dst_context)}
        return [rep]

    def ipbxcommand_meetme(self):
        return [{'amicommand': self._commanddict['function'].lower(),
                 'amiargs': self._commanddict['functionargs']}]

    def ipbxcommand_sipnotify(self):
        if 'variables' in self._commanddict:
            variables = self._commanddict.get('variables')
        channel = self._commanddict.get('channel')
        if channel == 'user:special:me':
            uinfo = self.rinnerdata.xod_config['users'].keeplist[self.userid]
            # TODO: Choose the appropriate line if more than one
            line = self.rinnerdata.xod_config['phones'].keeplist[uinfo['linelist'][0]]
            channel = line['identity'].replace('\\', '')
        reply = {'amicommand': 'sipnotify', 'amiargs': (channel, variables)}
        return [reply]

    def ipbxcommand_mailboxcount(self):
        """
        Send a MailboxCount ami command
        """
        if 'mailbox' in self._commanddict:
            return [{'amicommand': 'mailboxcount',
                      'amiargs': (self._commanddict['mailbox'],
                                    self._commanddict['context'])}]

    def ipbxcommand_transfer(self):
        try:
            dst = self.parseid(self._commanddict['destination'])
            transferers_channel = self.innerdata.find_users_channels_with_peer(self.userid)[0]
            channel = self.innerdata.channels[transferers_channel].peerchannel
            dst_context = self.innerdata.xod_config['phones'].get_main_line(self.userid)['context']

            if dst['type'] == 'user':
                extentodial = self.innerdata.xod_config['phones'].get_main_line(dst['id'])['number']
            elif dst['type'] == 'phone' and dst['id'] in self.innerdata.xod_config['phones'].keeplist:
                extentodial = self.innerdata.xod_config['phones'].keeplist[dst['id']]
            elif dst['type'] == 'exten':
                extentodial = dst['id']
            elif dst['type'] == 'voicemail' and dst['id'] in self.innerdata.xod_config['voicemails'].keeplist:
                # *97 vm number
                voicemail = self.innerdata.xod_config['voicemails'].keeplist[dst['id']]
                vm_number = voicemail['mailbox']
                prefix = self.innerdata.extenfeatures['extenfeatures']['vmboxslt']['exten']
                prefix = prefix[:len(prefix) - 1]
                extentodial = prefix + vm_number
                dst_context = voicemail['context']
            elif dst['type'] == 'meetme' and dst['id'] in self.innerdata.xod_config['meetmes'].keeplist:
                extentodial = self.innerdata.xod_config['meetmes'].keeplist[dst['id']]['confno']
            else:
                extentodial = None

            return [{'amicommand': 'transfer',
                      'amiargs': [channel, extentodial, dst_context]}]
        except KeyError:
            logger.exception('Failed to transfer call')
            return [{'error': 'Incomplete transfer information'}]

    def ipbxcommand_atxfer(self):
        try:
            exten = self.parseid(self._commanddict['destination'])['id']
            context = self.innerdata.xod_config['phones'].get_main_line(self.userid)['context']
            channel = self.innerdata.find_users_channels_with_peer(self.userid)[0]
        except KeyError:
            logger.exception('Atxfer failed %s', self._commanddict)
            return [{'error': 'Incomplete info'}]
        else:
            return [{'amicommand': 'atxfer',
                     'amiargs': [channel, exten, context]}]

    def ipbxcommand_intercept(self):
        try:
            main_line = self.innerdata.xod_config['phones'].get_main_line(self.userid)
            chan_xid = self._commanddict['tointercept']
            chan_id = self.parseid(chan_xid)['id']
            return [{'amicommand': 'transfer',
                     'amiargs': [chan_id,
                                 main_line['number'],
                                 main_line['context']]}]
        except KeyError:
            logger.warning('Failed to complete interception')
            return [{'error': 'Incomplete info'}]

    # hangup and one's own line management
    def ipbxcommand_hangup(self):
        channel = self.parseid(self._commanddict.get('channelids'))
        rep = {'amicommand': 'hangup',
               'amiargs': [channel.get('id')]}
        return [rep, ]

    def get_agent_info(self, command_dict):
        if 'agentids' not in command_dict or command_dict['agentids'] == 'agent:special:me':
            command_dict['agentids'] = self.innerdata.xod_config['users'].keeplist[self.userid]['agentid']
        if '/' in command_dict['agentids']:
            ipbx_id, agent_id = command_dict['agentids'].split('/', 1)
        else:
            ipbx_id, agent_id = self.ipbxid, command_dict['agentids']
        innerdata = self._ctiserver.safe
        if agent_id in innerdata.xod_config['agents'].keeplist:
            agent = innerdata.xod_config['agents'].keeplist[agent_id]
            status = innerdata.xod_status['agents'][agent_id]
            return agent, status

    def _get_agent_exten(self, command_dict, agent_id):
        if 'agentphonenumber' in command_dict:
            return command_dict['agentphonenumber']
        user_ids = [user['id'] for user in self.innerdata.xod_config['users'].keeplist.itervalues() if user['agentid'] == str(agent_id)]
        return self.innerdata.xod_config['phones'].get_main_line(user_ids[0])['number'] if user_ids else None

    def ipbxcommand_record(self):
        subcommand = self._commanddict.pop('subcommand')
        channel = self._commanddict.pop('channel')
        # XX take into account ipbxid
        if subcommand == 'start':
            datestring = time.strftime('%Y%m%d-%H%M%S', time.localtime())
            # kind agent => channel = logged-on channel
            # other kind => according to what is provided
            kind = 'phone'
            idv = '7'
            filename = 'cti-monitor-%s-%s-%s' % (datestring, kind, idv)
            rep = {'amicommand': 'monitor',
                   'amiargs': (channel, filename, 'false')}
            # wait the AMI event ack in order to fill status for channel
        elif subcommand == 'stop':
            rep = {'amicommand': 'stopmonitor',
                   'amiargs': (channel,)}
        return [rep]

    def ipbxcommand_listen(self):
        start = self._commanddict['subcommand'] == 'start'
        listeners_line = self.innerdata.xod_config['phones'].get_main_line(self.userid)
        listener_protocol = listeners_line['protocol']
        listener_name = listeners_line['name']
        agent_id = '/'.join(self._commanddict['destination'].split('/')[1:])
        agent_config = self.innerdata.xod_config['agents'].keeplist[agent_id]
        agent_number = agent_config['number']
        channel = 'Agent/%s' % agent_number

        rep = {}

        if start:
            rep = {'amicommand': 'origapplication',
                   'amiargs': ['ChanSpy',
                               '%s,d' % channel,
                               listener_protocol,
                               listener_name,
                               '000',
                               'mamaop']}

        return [rep]
