# -*- coding: utf-8 -*-
# Copyright (C) 2013-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_cti.cti.cti_command import CTICommandClass


SubscribeToQueuesStats = CTICommandClass('subscribetoqueuesstats', None, None)
SubscribeToQueuesStats.add_to_registry()
