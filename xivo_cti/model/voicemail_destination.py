# -*- coding: utf-8 -*-

# Copyright (C) 2013-2014 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

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
