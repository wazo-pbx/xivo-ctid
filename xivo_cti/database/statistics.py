# -*- coding: utf-8 -*-

# Copyright (C) 2016 Avencall
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

from datetime import datetime

from xivo_dao.alchemy.stat_switchboard_queue import StatSwitchboardQueue
from xivo_dao.alchemy.queuefeatures import QueueFeatures

from xivo_dao.helpers.db_utils import session_scope


def insert_switchboard_call(time, state, wait_time, queue_name):
    with session_scope() as session:
        queue_id = session.query(QueueFeatures.id).filter(
            QueueFeatures.name == queue_name
        ).scalar()
        stat = StatSwitchboardQueue(time=datetime.fromtimestamp(time),
                                    end_type=state,
                                    wait_time=wait_time,
                                    queue_id=queue_id)
        session.add(stat)
