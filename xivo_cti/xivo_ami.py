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
import os
import socket
import subprocess
import time
import errno

from copy import copy

from xivo.xivo_helpers import clean_extension
from xivo_dao import extensions_dao

from xivo_cti import config
from xivo_cti.tools.extension import normalize_exten
from xivo_cti.interfaces.interface_ami import AMI

logger = logging.getLogger('xivo_ami')

switch_originates = True


class AMIClass(object):
    class AMIError(Exception):
        pass

    def __init__(self):
        ipbxconfig = config['ipbx_connection']
        self.ipbxid = 'xivo'
        self.ipaddress = ipbxconfig.get('ipaddress', '127.0.0.1')
        self.ipport = int(ipbxconfig.get('ipport', 5038))
        self.loginname = ipbxconfig.get('username', 'xivouser')
        self.password = ipbxconfig.get('password', 'xivouser')
        self.actionid = None

    def connect(self):
        self.actionid = None
        if os.environ.get('XIVO_CTID_AMI_PROXY'):
            logger.info('Connecting to AMI through ami-proxy...')
            try:
                self.sock = self._new_connection_with_ami_proxy()
            except Exception:
                logger.exception('Could not connect to AMI through ami-proxy')
                self.sock = self._new_connection()
        else:
            self.sock = self._new_connection()
        self.sock.settimeout(30)
        self.fd = self.sock.fileno()

    def _new_connection(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sockret = sock.connect_ex((self.ipaddress, self.ipport))
        if sockret:
            logger.warning('unable to connect to %s:%d - reason %d',
                           self.ipaddress, self.ipport, sockret)
            raise self.AMIError('failed to connect')
        return sock

    def _new_connection_with_ami_proxy(self):
        sock1, sock2 = socket.socketpair(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            subprocess.Popen(['ami-proxy', self.ipaddress, str(self.ipport)], stdin=sock2, stdout=sock2, close_fds=True)
        except Exception:
            sock1.close()
            sock2.close()
            raise

        sock2.close()
        return sock1

    def sendcommand(self, action, args, loopnum=0):
        ret = False
        try:
            t0 = time.time()
            towritefields = ['Action: %s' % action]
            for (name, value) in args:
                towritefields.append('%s: %s' % (name, value))
            if self.actionid:
                towritefields.append('ActionId: %s' % self.actionid)
            towritefields.append('\r\n')

            rawstr = '\r\n'.join(towritefields)
            if isinstance(rawstr, unicode):
                ustr = rawstr.encode('utf8')
            else:
                ustr = rawstr
            self.sock.sendall(ustr)
            ret = True
        except UnicodeEncodeError:
            logger.exception('(sendcommand UnicodeEncodeError (%s %s %s))',
                             towritefields, self.actionid, self.fd)
            ret = True
        except UnicodeDecodeError:
            logger.exception('(sendcommand UnicodeDecodeError (%s %s %s))',
                             action, self.actionid, self.fd)
            ret = True
        except socket.timeout:
            t1 = time.time()
            logger.exception('(sendcommand timeout (%s %s %s) timespent=%f)',
                             action, self.actionid, self.fd, (t1 - t0))
            ret = False
        except socket.error, e:
            t1 = time.time()
            logger.exception('(sendcommand socket error (%s %s %s) timespent=%f)',
                             action, self.actionid, self.fd, (t1 - t0))
            ret = False
        except IOError, e:
            t1 = time.time()
            if e.errno == errno.EPIPE:
                logger.exception('(sendcommand I/O Error EPIPE (%s %s %s) timespent=%f)',
                                 action, self.actionid, self.fd, (t1 - t0))
            else:
                logger.exception('(sendcommand I/O Error Other (%s %s %s) timespent=%f)',
                                 action, self.actionid, self.fd, (t1 - t0))
            ret = False
        if self.actionid:
            self.actionid = None
        return ret

    def setactionid(self, actionid):
        self.actionid = actionid

    def _exec_command(self, *args):
        return self.sendcommand(*args)

    def sendqueuestatus(self, queue=None):
        if queue is None:
            return self._exec_command('QueueStatus', [])
        else:
            return self._exec_command('QueueStatus',
                                      [('Queue', queue)])

    # \brief Requesting an ExtensionState.
    def sendextensionstate(self, exten, context):
        return self._exec_command('ExtensionState',
                                  [('Exten', exten),
                                   ('Context', context)])

    # \brief Logins to the AMI.
    def login(self):
        return self._exec_command('Login',
                                  [('Username', self.loginname),
                                   ('Secret', self.password)])

    def hangup(self, channel):
        return self._hangup(channel, None)

    def hangup_with_cause_answered_elsewhere(self, channel):
        # On most SIP phones, hanging up a ringing call with the cause
        # "answered elsewhere" prevents the phone from displaying the call
        # as a missed call.
        return self._hangup(channel, '26')

    def _hangup(self, channel, cause):
        command_details = [('Channel', channel)]
        if cause:
            command_details.append(('Cause', cause))
        return self._exec_command('Hangup', command_details)

    def setvar(self, var, val, chan=None):
        if chan is None:
            return self._exec_command('Setvar', [('Variable', var),
                                                 ('Value', val)])
        else:
            return self._exec_command('Setvar', [('Channel', chan),
                                                 ('Variable', var),
                                                 ('Value', val)])

    def redirect(self, channel, context, exten='s', priority='1'):
        return self._exec_command('Redirect',
                                  [('Channel', channel),
                                   ('Context', context),
                                   ('Exten', exten),
                                   ('Priority', priority)])

    # \brief Originates a call from a phone towards another.
    def originate(self, phoneproto, phonesrcname, phonesrcnum, cidnamesrc,
                  phonedst, cidnamedst,
                  locext, extravars={}, timeout=3600):
        # originate a call btw src and dst
        # src will ring first, and dst will ring when src responds
        phonedst = normalize_exten(phonedst)
        if phoneproto == 'custom':
            channel = phonesrcname.replace('\\', '')
        else:
            channel = '%s/%s' % (phoneproto.upper(), phonesrcname)
        command_details = [('Channel', channel),
                           ('Exten', phonedst),
                           ('Context', locext),
                           ('Priority', '1'),
                           ('Timeout', str(timeout * 1000)),
                           ('Variable', 'XIVO_ORIGAPPLI=%s' % 'OrigDial'),
                           ('Variable', 'XIVO_ORIG_CID_NAME=%s' % cidnamesrc),
                           ('Variable', 'XIVO_ORIG_CID_NUM=%s' % phonesrcnum),
                           ('Async', 'true')]
        if switch_originates:
            if (phonedst.startswith('#')):
                command_details.append(('CallerID', '"%s" <>' % cidnamedst))
            else:
                command_details.append(('CallerID', '"%s"<%s>' % (cidnamedst, phonedst)))
        else:
            command_details.append(('CallerID', '"%s"' % cidnamesrc))
        for var, val in extravars.iteritems():
            command_details.append(('Variable', '%s=%s' % (var, val)))

        action_id = AMI.make_actionid()
        self.actionid = copy(action_id)

        self._exec_command('Originate', command_details)

        return action_id

    # \brief Requests the Extension Statuses
    def extensionstate(self, extension, context):
        return self._exec_command('ExtensionState', [('Exten', extension),
                                                     ('Context', context)])

    def meetmemute(self, meetme, usernum):
        self._exec_command('MeetmeMute', (('Meetme', meetme),
                                          ('Usernum', usernum)))

    def meetmeunmute(self, meetme, usernum):
        self._exec_command('MeetmeUnmute', (('Meetme', meetme),
                                            ('Usernum', usernum)))

    def queueadd(self, queuename, interface, paused, skills=''):
        # it looks like not specifying Paused is the same as setting it to false
        return self._exec_command('QueueAdd', [('Queue', queuename),
                                               ('Interface', interface),
                                               ('Penalty', '1'),
                                               ('Paused', paused),
                                               ('Skills', skills)])

    # \brief Removes a Queue
    def queueremove(self, queuename, interface):
        return self._exec_command('QueueRemove', [('Queue', queuename),
                                                  ('Interface', interface)])

    # \brief (Un)Pauses a Queue
    def queuepause(self, queuename, interface, paused):
        return self._exec_command('QueuePause', [('Queue', queuename),
                                                 ('Interface', interface),
                                                 ('Paused', paused)])

    def queuepauseall(self, interface, paused):
        return self._exec_command('QueuePause', [('Interface', interface),
                                                 ('Paused', paused)])

    # \brief Logs a Queue Event
    def queuelog(self, queuename, event,
                 uniqueid=None,
                 interface=None,
                 message=None):
        command_details = [('Queue', queuename),
                           ('Event', event)]
        if uniqueid:
            command_details.append(('Uniqueid', uniqueid))
        if interface:
            command_details.append(('Interface', interface))
        if message:
            command_details.append(('Message', message))
        return self._exec_command('QueueLog', command_details)

    def queuestatus(self, queue_name=None, member_name=None):
        command_details = []
        if queue_name is not None:
            command_details.append(('Queue', queue_name))
        if member_name is not None:
            command_details.append(('Member', member_name))
        return self._exec_command('QueueStatus', command_details)

    def queuesummary(self, queuename=None):
        if queuename is None:
            return self._exec_command('QueueSummary', [])
        else:
            return self._exec_command('QueueSummary', [('Queue', queuename)])

    # \brief Requests the Mailbox informations
    def mailbox(self, phone, context):
        ret1 = self._exec_command('MailboxCount', [('Mailbox', '%s@%s' % (phone, context))])
        ret2 = self._exec_command('MailboxStatus', [('Mailbox', '%s@%s' % (phone, context))])
        ret = ret1 and ret2
        return ret

    def sipnotify(self, channel, variables):
        if not variables or not channel:
            raise ValueError('Missing fields to send a SIPNotify')

        arg_list = [('Channel', channel)]
        arg_list.extend(('Variable', '%s=%s' % (name, value)) for name, value in variables.iteritems())

        return self._exec_command('SIPNotify', arg_list)

    # \brief Request a mailbox count
    # context is for tracking only
    def mailboxcount(self, mailbox, context=None):
        full_mailbox = mailbox
        if context:
            full_mailbox = "%s@%s" % (mailbox, context)
        return self._exec_command('MailboxCount', (('MailBox', full_mailbox),))

    def transfer(self, channel, extension, context):
        try:
            extension = normalize_exten(extension)
        except ValueError, e:
            logger.warning('Transfer failed: %s', e.message)
            return False
        else:
            self.setvar('BLINDTRANSFER', 'true', channel)
        return self.redirect(channel, context, extension)

    def voicemail_atxfer(self, channel, context, voicemail_number):
        logger.debug('voicemail_atxfer: channel: %s context: %s voicemail %s',
                     channel, context, voicemail_number)

        prefix = clean_extension(extensions_dao.exten_by_name('vmboxslt'))
        consult_vm_exten = '{}{}#'.format(prefix, voicemail_number)

        return self.atxfer(channel, consult_vm_exten, context)

    def voicemail_transfer(self, channel, base_context, voicemail_number):
        logger.debug('voicemail_transfer: channel: %s context: %s voicemail %s',
                     channel, base_context, voicemail_number)

        self.setvar('XIVO_BASE_CONTEXT', base_context, channel)
        self.setvar('ARG1', voicemail_number, channel)
        return self.redirect(channel, 'vmbox')

    def atxfer(self, channel, extension, context):
        try:
            extension = normalize_exten(extension)
        except ValueError, e:
            logger.warning('Attended transfer failed: %s', e.message)
            return False
        else:
            return self._exec_command('Atxfer', [('Channel', channel),
                                                 ('Exten', extension),
                                                 ('Context', context),
                                                 ('Priority', '1')])

    def switchboard_retrieve(self, line_interface, channel, cid_name, cid_num, cid_name_src, cid_num_src):
        self._exec_command('Originate',
                           [('Channel', line_interface),
                            ('Exten', 's'),
                            ('Context', 'xivo_switchboard_retrieve'),
                            ('Priority', '1'),
                            ('CallerID', '"%s" <%s>' % (cid_name, cid_num)),
                            ('Variable', 'XIVO_CID_NUM=%s' % cid_num),
                            ('Variable', 'XIVO_CID_NAME=%s' % cid_name),
                            ('Variable', 'XIVO_ORIG_CID_NUM=%s' % cid_num_src),
                            ('Variable', 'XIVO_ORIG_CID_NAME=%s' % cid_name_src),
                            ('Variable', 'XIVO_CHANNEL=%s' % channel),
                            ('Async', 'true')])

    def txfax(self, faxpath, userid, callerid, number, context):
        # originate a call btw src and dst
        # src will ring first, and dst will ring when src responds
        try:
            ret = self.sendcommand('Originate', [('Channel', 'Local/%s@%s' % (number, context)),
                                                 ('CallerID', callerid),
                                                 ('Variable', 'XIVO_FAX_PATH=%s' % faxpath),
                                                 ('Variable', 'XIVO_USERID=%s' % userid),
                                                 ('Context', 'txfax'),
                                                 ('Exten', 's'),
                                                 ('Async', 'true'),
                                                 ('Priority', '1')])
            return ret
        except self.AMIError:
            return False
        except socket.timeout:
            return False
        except socket:
            return False
