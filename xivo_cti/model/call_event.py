# -*- coding: utf-8 -*-
# Copyright (C) 2007-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

from collections import namedtuple

CallEvent = namedtuple('CallEvent', ['uniqueid', 'source', 'destination', 'status'])
