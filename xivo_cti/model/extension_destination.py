# -*- coding: utf-8 -*-
# Copyright (C) 2013-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_cti.model.destination import Destination


class ExtensionDestination(Destination):

    def to_exten(self):
        return self.value
