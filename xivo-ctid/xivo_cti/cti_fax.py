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

import base64
import commands
import logging
import os
import threading

logger = logging.getLogger('async')

PATH_SPOOL_ASTERISK = '/var/spool/asterisk'
PATH_SPOOL_ASTERISK_FAX = PATH_SPOOL_ASTERISK + '/fax'
PATH_SPOOL_ASTERISK_TMP = PATH_SPOOL_ASTERISK + '/tmp'
PDF2FAX = '/usr/bin/xivo_pdf2fax'


class asyncActionsThread(threading.Thread):
    def __init__(self, name, params):
        threading.Thread.__init__(self)
        self.setName(name)
        self.params = params

    def decodefile(self):
        decodedfile = base64.b64decode(self.params.get('rawfile').strip())
        filename = 'astsendfax-%s' % self.params.get('fileid')
        self.tmpfilepath = '%s/%s' % (PATH_SPOOL_ASTERISK_TMP, filename)
        z = open(self.tmpfilepath, 'w')
        z.write(decodedfile)
        z.close()

    def converttotiff(self):
        reply = 'ko;unknown'
        comm = commands.getoutput('file -b %s' % self.tmpfilepath)
        brieffile = ' '.join(comm.split()[0:2])
        if brieffile == 'PDF document,':
            self.faxfilepath = self.tmpfilepath + '.tif'
            pdf2fax_command = '%s -o %s %s' % (PDF2FAX, self.faxfilepath, self.tmpfilepath)
            logger.info('(ref %s) PDF to TIF(F) : %s', self.tmpfilepath, pdf2fax_command)
            reply = 'ko;convert-pdftif'
            sysret = os.system(pdf2fax_command)
            ret = os.WEXITSTATUS(sysret)
            if ret:
                logger.warning('(ref %s) PDF to TIF(F) returned : %s (exitstatus = %s, stopsignal = %s)',
                               self.tmpfilepath, sysret, ret, os.WSTOPSIG(sysret))
            else:
                reply = 'ok;'
        else:
            reply = 'ko;filetype'
            logger.warning('(ref %s) the file received is a <%s> one : format not supported',
                           self.tmpfilepath, brieffile)
            ret = -1
        print reply
        os.unlink(self.tmpfilepath)

    def notify_step(self, stepname):
        innerdata = self.params.get('innerdata')
        fileid = self.params.get('fileid')
        innerdata.cb_timer({'action': 'fax',
                            'properties': {'step': stepname,
                                           'fileid': fileid}},)

    def run(self):
        self.decodefile()
        self.notify_step('file_decoded')
        self.converttotiff()
        self.notify_step('file_converted')


class Fax(object):
    def __init__(self, innerdata, fileid):
        self.innerdata = innerdata
        self.fileid = fileid

        filename = 'astsendfax-%s' % self.fileid
        self.faxfilepath = '%s/%s.tif' % (PATH_SPOOL_ASTERISK_TMP, filename)

    def setfaxparameters(self, userid, context, number, hide):
        self.userid = userid
        self.context = context
        self.number = number.replace('.', '').replace(' ', '')
        linelist = self.innerdata.xod_config['users'].keeplist[userid]['linelist']
        if not linelist or hide != '0':
            self.callerid = 'anonymous'
        else:
            phoneid = linelist[0]
            self.callerid = self.innerdata.xod_config['phones'].get_callerid_from_phone_id(phoneid)

    def setfileparameters(self, size):
        self.size = size

    def setsocketref(self, socketref):
        self.socketref = socketref

    def setrequester(self, requester):
        self.requester = requester

    def setbuffer(self, rawfile):
        """Set on the 2nd opened soocket"""
        self.rawfile = rawfile

    def launchasyncs(self):
        sthread = asyncActionsThread('fax-%s' % self.fileid,
                                     {'innerdata' : self.innerdata,
                                      'fileid' : self.fileid,
                                      'rawfile' : self.rawfile
                                      })
        sthread.start()

    def step(self, stepname):
        removeme = False
        try:
            self.requester.reply({'class' : 'faxsend',
                                  'fileid' : self.fileid,
                                  'step' : stepname
                                  })
        except Exception:
            # when requester is not connected any more ...
            pass

        if stepname == 'file_converted':
            removeme = True

        return removeme

    def getparams(self):
        params = {
            'mode' : 'useraction',
            'request' : {
                'requester' : self.requester,
                'ipbxcommand' : 'sendfax',
                'commandid' : self.fileid
                },
            'amicommand' : 'txfax',
            'amiargs' : (self.faxfilepath,
                         self.userid,
                         self.callerid,
                         self.number,
                         self.context)
            }
        return params
