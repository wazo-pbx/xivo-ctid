# -*- coding: utf-8 -*-
# Copyright (C) 2007-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_cti.cti.cti_command import CTICommandClass


CancelTransfer = CTICommandClass('cancel_transfer', None, None)
CancelTransfer.add_to_registry()
