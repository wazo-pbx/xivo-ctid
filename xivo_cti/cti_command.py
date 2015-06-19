# -*- coding: utf-8 -*-

# Copyright (C) 2007-2015 Avencall
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
import random

from xivo_cti import ALPHANUMS
from xivo_cti import cti_fax, dao
from xivo_cti import config
from xivo_cti.ioc.context import context as cti_context
from xivo_cti.statistics.queue_statistics_encoder import QueueStatisticsEncoder
from xivo_dao import extensions_dao

logger = logging.getLogger('cti_command')

LOGINCOMMANDS = [
    'login_pass', 'login_capas'
]

REGCOMMANDS = [
    'getipbxlist',
    'keepalive',

    'faxsend',
    'filetransfer',
    'chitchat',

    'getqueuesstats',

    'ipbxcommand'
]

IPBXCOMMANDS = [
    'originate',
    # transfer-like commands
    'intercept',
    'transfer', 'atxfer',
    # hangup-like commands
    'hangup',

    'mailboxcount',
    'meetme',
]


class Command(object):
    def __init__(self, connection, thiscommand):
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

        self.user_keeplist = self.innerdata.xod_config['users'].keeplist.get(self.userid)

        messagebase = {'class': self.command}

        if self.commandid:
            messagebase['replyid'] = self.commandid

        if self.command in REGCOMMANDS and not self._connection.connection_details.get('logged'):
            messagebase['error_string'] = 'notloggedyet'
        elif self.command in LOGINCOMMANDS or self.command in REGCOMMANDS:
            methodname = 'regcommand_%s' % self.command
            if hasattr(self, methodname):
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
        self.head = 'LOGINFAIL - login_pass'
        # user authentication
        missings = []
        for argum in ['hashedpassword']:
            if argum not in self._commanddict:
                missings.append(argum)
        if missings:
            logger.warning('%s - missing args : %s', self.head, missings)
            return 'missing:%s' % ','.join(missings)

        if self._is_user_authenticated():
            self._connection.connection_details['authenticated'] = True
        else:
            return 'login_password'

        cti_profile_id = self.user_keeplist['cti_profile_id']
        if cti_profile_id is None:
            logger.warning("%s - No CTI profile defined for the user", self.head)
            return 'capaid_undefined'
        else:
            return {'capalist': [cti_profile_id]}

    def _is_user_authenticated(self):
        this_hashed_password = self._commanddict.get('hashedpassword')
        cdetails = self._connection.connection_details
        sessionid = cdetails.get('prelogin').get('sessionid')

        if self.ipbxid and self.userid:
            ref_hashed_password = self._ctiserver.safe.user_get_hashed_password(self.userid, sessionid)
            if ref_hashed_password != this_hashed_password:
                logger.warning('%s - wrong hashed password', self.head)
                return False
            else:
                return True
        else:
            logger.warning('%s - undefined user : probably the login_id step failed', self.head)
            return False

    def regcommand_login_capas(self):
        self.head = 'LOGINFAIL - login_capas'
        missings = []
        for argum in ['state', 'capaid', 'lastconnwins', 'loginkind']:
            if argum not in self._commanddict:
                missings.append(argum)
        if missings:
            logger.warning('%s - missing args : %s', self.head, missings)
            return 'missing:%s' % ','.join(missings)

        cdetails = self._connection.connection_details

        state = self._commanddict.get('state')
        capaid = self._commanddict.get('capaid')

        iserr = self.__check_capa_connection__(capaid)
        if iserr is not None:
            logger.warning('%s - wrong capaid : %s %s', self.head, iserr, capaid)
            return iserr

        self.__connect_user__(state, capaid)
        self.head = 'LOGIN SUCCESSFUL'
        logger.info('%s for %s', self.head, cdetails)

        cti_profile_id = self.user_keeplist['cti_profile_id']
        profilespecs = config['profiles'].get(cti_profile_id)

        capastruct = {}
        summarycapas = {}
        if profilespecs:
            for capakind in ['regcommands', 'ipbxcommands',
                             'services', 'preferences',
                             'userstatus', 'phonestatus']:
                if profilespecs.get(capakind):
                    tt = profilespecs.get(capakind)
                    cfg_capakind = config[capakind]
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
                 'capas': capastruct}

        self._connection.connection_details['logged'] = True
        self._connection.login_task.cancel()
        return reply

    def __check_capa_connection__(self, capaid):
        cdetails = self._connection.connection_details
        userid = cdetails.get('userid')
        capaid = int(capaid)

        if capaid not in config['profiles'].keys():
            return 'unknown cti_profile_id'
        if capaid != self._ctiserver.safe.xod_config['users'].keeplist[userid]['cti_profile_id']:
            return 'wrong cti_profile_id'

    def __connect_user__(self, availstate, c):
        user_service_manager = cti_context.get('user_service_manager')
        cdetails = self._connection.connection_details
        userid = cdetails.get('userid')
        self._ctiserver.safe.xod_status['users'][userid]['connection'] = 'yes'
        user_service_manager.set_presence(userid, availstate)

    # end of login/logout related commands

    def regcommand_chitchat(self):
        reply = {}
        chitchattext = self._commanddict.get('text')
        self._othermessages.append({'dest': self._commanddict.get('to'),
                                   'message': {'to': self._commanddict.get('to'),
                                               'from': '%s/%s' % (self.ripbxid, self.ruserid),
                                               'text': chitchattext}})
        return reply

    def regcommand_getqueuesstats(self):
        if 'on' not in self._commanddict:
            return {}
        statistic_results = {}
        for queue_id, params in self._commanddict['on'].iteritems():
            queue_name = dao.queue.get_name_from_id(queue_id)
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
            if function == 'put_announce':
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

        if not self.ipbxcommand or self.ipbxcommand not in IPBXCOMMANDS:
            return reply

        reply['command'] = self.ipbxcommand

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
                ipbxreply = self._ctiserver.interface_ami.execute_and_track(actionid, params)
            else:
                ipbxreply = z.get('error')
            idz += 1

        reply['ipbxreply'] = ipbxreply
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
                exten = extensions_dao.exten_by_name('vmusermsg')
                vm = innerdata.xod_config['voicemails'].keeplist[dst['id']]
                extentodial = exten
                dst_context = vm['context']
                dst_identity = 'Voicemail'
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
                voicemail = self.innerdata.xod_config['voicemails'].keeplist[dst['id']]
                vm_number = voicemail['mailbox']
                prefix = extensions_dao.exten_by_name('vmboxslt')
                extentodial = prefix[:-1] + vm_number
                dst_context = voicemail['context']
            elif dst['type'] == 'meetme' and dst['id'] in self.innerdata.xod_config['meetmes'].keeplist:
                extentodial = self.innerdata.xod_config['meetmes'].keeplist[dst['id']]['confno']
            else:
                extentodial = None

            return [{'amicommand': 'transfer',
                     'amiargs': [channel, extentodial, dst_context]}]
        except (KeyError, IndexError):
            logger.exception('Failed to transfer call')
            return [{'error': 'Incomplete transfer information'}]

    def ipbxcommand_atxfer(self):
        try:
            exten = self.parseid(self._commanddict['destination'])['id']
            context = self.innerdata.xod_config['phones'].get_main_line(self.userid)['context']
            channel = self.innerdata.find_users_channels_with_peer(self.userid)[0]
        except (KeyError, IndexError):
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
