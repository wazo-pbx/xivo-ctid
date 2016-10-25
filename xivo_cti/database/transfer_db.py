# -*- coding: utf-8 -*-

# Copyright (C) 2016 Proformatique Inc.
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

from sqlalchemy import and_
from xivo_dao.alchemy.features import Features
from xivo_dao.helpers.db_utils import session_scope


def get_transfer_dial_timeout():
    with session_scope() as session:
        query = session.query(Features.var_val).filter(
            and_(Features.category == 'general',
                 Features.var_name == 'atxfernoanswertimeout'))
        timeout_str = query.scalar()
        return int(timeout_str)
