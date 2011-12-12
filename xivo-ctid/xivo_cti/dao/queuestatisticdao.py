# -*- coding: UTF-8 -*-

import time
from xivo_cti.dao.alchemy.queueinfo import QueueInfo
from xivo_cti.dao.alchemy import dbconnection
from sqlalchemy import or_
from sqlalchemy.sql.expression import func


def _get_session():
    return dbconnection.get_connection('queue_stats').get_session()


class QueueStatisticDAO(object):
    def get_received_call_count(self, queue_name, window):
        in_window = self._compute_window_time(window)
        return (_get_session().query(QueueInfo)
                .filter(QueueInfo.queue_name == queue_name)
                .filter(QueueInfo.call_time_t > in_window).count())

    def get_answered_call_count(self, queue_name, window):
        in_window = self._compute_window_time(window)
        return (_get_session().query(QueueInfo).filter(QueueInfo.queue_name == queue_name)
                .filter(QueueInfo.call_time_t > in_window).filter(QueueInfo.call_picker != '').count())

    def get_abandonned_call_count(self, queue_name, window):
        in_window = self._compute_window_time(window)
        return (_get_session().query(QueueInfo)
                .filter(QueueInfo.queue_name == queue_name)
                .filter(QueueInfo.call_time_t > in_window)
                .filter(or_(QueueInfo.call_picker == '', QueueInfo.call_picker == None))
                .filter(QueueInfo.hold_time != None).count())

    def get_answered_call_in_qos_count(self, queue_name, window, xqos):
        in_window = self._compute_window_time(window)
        return (_get_session().query(QueueInfo)
                .filter(QueueInfo.queue_name == queue_name)
                .filter(QueueInfo.call_time_t > in_window)
                .filter(QueueInfo.call_picker != '')
                .filter(QueueInfo.hold_time <= xqos).count())

    def get_received_and_done(self, queue_name, window):
        in_window = self._compute_window_time(window)
        return (_get_session().query(QueueInfo)
                .filter(QueueInfo.queue_name == queue_name)
                .filter(QueueInfo.call_time_t > in_window)
                .filter(QueueInfo.hold_time != None).count())

    def get_max_hold_time(self, queue_name, window):
        in_window = self._compute_window_time(window)
        return (_get_session().query(func.max(QueueInfo.hold_time))
                .filter(QueueInfo.queue_name == queue_name)
                .filter(QueueInfo.call_time_t > in_window)).one()[0]

    def _compute_window_time(self, window):
        return time.time() - window