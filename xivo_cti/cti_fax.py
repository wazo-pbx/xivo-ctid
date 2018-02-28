# -*- coding: utf-8 -*-
# Copyright (C) 2007-2015 Avencall
# Copyright (C) 2016 Proformatique Inc.
# SPDX-License-Identifier: GPL-3.0+

import base64
import commands
import logging
import os
import threading

from xivo_cti.ioc.context import context

logger = logging.getLogger(__name__)

PATH_SPOOL = '/var/spool/xivo-ctid/fax'
PDF2FAX = '/usr/bin/xivo_pdf2fax'


class asyncActionsThread(threading.Thread):

    def __init__(self, name, params):
        threading.Thread.__init__(self)
        self.setName(name)
        self.params = params
        self._task_queue = context.get('task_queue')

    def decodefile(self):
        decodedfile = base64.b64decode(self.params.get('rawfile').strip())
        filename = 'astsendfax-%s' % self.params.get('fileid')
        self.tmpfilepath = '%s/%s' % (PATH_SPOOL, filename)
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
        self._task_queue.put(innerdata.send_fax, stepname, fileid)

    def run(self):
        self.decodefile()
        self.converttotiff()
        self.notify_step('file_converted')


class Fax(object):

    def __init__(self, innerdata, fileid, data):
        self.innerdata = innerdata
        self.fileid = fileid
        self.rawfile = data
        self.callerid = 'anonymous'

        filename = 'astsendfax-%s' % self.fileid
        self.faxfilepath = '%s/%s.tif' % (PATH_SPOOL, filename)

    def setfaxparameters(self, userid, context, number):
        self.userid = userid
        self.context = context
        self.number = number.replace('.', '').replace(' ', '')
        phone_ids = self.innerdata.xod_config['users'].keeplist[userid]['linelist']
        if phone_ids:
            try:
                self.callerid = self.innerdata.xod_config['phones'].get_callerid_from_phone_id(phone_ids[0])
            except KeyError:
                # stays anonymous
                pass

    def setrequester(self, requester):
        self.requester = requester

    def launchasyncs(self):
        sthread = asyncActionsThread('fax-%s' % self.fileid,
                                     {'innerdata': self.innerdata,
                                      'fileid': self.fileid,
                                      'rawfile': self.rawfile})
        sthread.start()

    def step(self, stepname):
        removeme = False
        if stepname == 'file_converted':
            removeme = True

        return removeme

    def getparams(self):
        params = {
            'mode': 'useraction',
            'request': {
                'requester': self.requester,
                'ipbxcommand': 'sendfax',
                'commandid': self.fileid
            },
            'amicommand': 'txfax',
            'amiargs': (self.faxfilepath,
                        self.userid,
                        self.callerid,
                        self.number,
                        self.context)
        }
        return params
