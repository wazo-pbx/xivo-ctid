# -*- coding: utf-8 -*-
# Copyright (C) 2013-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.helpers.db_utils import session_scope
from xivo_cti.model.destination import Destination
from xivo_dao import extensions_dao
from xivo_cti import dao


class VoicemailDestination(Destination):

    def to_exten(self):
        with session_scope():
            call_vm_exten = extensions_dao.exten_by_name('vmboxslt')
        vm_number = dao.voicemail.get_number(self.value)
        return call_vm_exten.replace('.', vm_number)
