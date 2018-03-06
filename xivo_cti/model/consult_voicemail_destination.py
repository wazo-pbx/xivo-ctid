# -*- coding: utf-8 -*-
# Copyright (C) 2013-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.helpers.db_utils import session_scope
from xivo_cti.model.destination import Destination
from xivo_dao import extensions_dao


class ConsultVoicemailDestination(Destination):

    def to_exten(self):
        with session_scope():
            return extensions_dao.exten_by_name('vmusermsg')
