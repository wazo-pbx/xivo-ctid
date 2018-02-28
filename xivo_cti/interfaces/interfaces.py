# -*- coding: utf-8 -*-
# Copyright (C) 2007-2016 Avencall
# SPDX-License-Identifier: GPL-3.0+


class DisconnectCause(object):

    by_client = 'by_client'
    by_server_stop = 'by_server_stop'
    by_server_reload = 'by_server_reload'
    broken_pipe = 'broken_pipe'

    @classmethod
    def is_valid(cls, cause):
        return cause in [cls.by_client, cls.by_server_stop, cls.by_server_reload, cls.broken_pipe]


class Interfaces(object):

    def __init__(self, ctiserver):
        self._ctiserver = ctiserver
        self.connid = None
        self.requester = None

    def connected(self, connid):
        self.connid = connid
        self.requester = connid.getpeername()[:2]

    def disconnected(self, cause):
        self.connid = None
        self.requester = None
