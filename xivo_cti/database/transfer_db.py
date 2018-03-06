# -*- coding: utf-8 -*-
# Copyright (C) 2016 Proformatique Inc.
# SPDX-License-Identifier: GPL-3.0+

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
