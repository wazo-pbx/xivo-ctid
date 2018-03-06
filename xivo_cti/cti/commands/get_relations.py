# -*- coding: utf-8 -*-
# Copyright (C) 2015 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_cti.cti.cti_command import CTICommandClass


GetRelations = CTICommandClass('get_relations', None, None)
GetRelations.add_to_registry()
