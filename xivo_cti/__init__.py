# -*- coding: utf-8 -*-
# Copyright 2013-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import ssl
import string

from UserDict import UserDict

__all__ = []

CTI_PROTOCOL_VERSION = '2.3'
DAEMONNAME = 'xivo-ctid'
SSLPROTO = ssl.PROTOCOL_TLSv1
ALPHANUMS = string.uppercase + string.lowercase + string.digits

config = UserDict()
