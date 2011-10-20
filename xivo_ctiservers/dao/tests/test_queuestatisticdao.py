
import unittest
from xivo_ctiservers.dao.alchemy.queueinfo import QueueInfo
from xivo_ctiservers.dao.alchemy.base import Base
import time
from xivo_ctiservers.dao.queuestatisticdao import QueueStatisticDAO
from xivo_ctiservers.dao.alchemy.dbconnection import DBConnection


class Test(unittest.TestCase):


    def setUp(self):
        uri = 'postgresql://asterisk:asterisk@localhost/asterisktest'
        connection = DBConnection(uri)
        connection.connect()

        Base.metadata.drop_all(connection.getEngine(), [QueueInfo().__table__])
        Base.metadata.create_all(connection.getEngine(), [QueueInfo().__table__])

        self.session = connection.getSession()

        self.session.commit()
        self._queue_statistic_dao = QueueStatisticDAO()
        self._queue_statistic_dao._session = self.session

    def tearDown(self):
        DBConnection.close()

    def _insert_received_calls(self, window, nb_in_window, queue_name):
        out_of_window_delta = window + 30
        in_window = time.time()
        count_out_window = 3
        out_of_window = time.time() - out_of_window_delta
        for i in range(nb_in_window):
            queueinfo = QueueInfo()
            queueinfo.call_time_t = in_window
            queueinfo.queue_name = queue_name
            self.session.add(queueinfo)
            queueinfo.call_picker = ''
        for i in range(count_out_window):
            queueinfo = QueueInfo()
            queueinfo.call_time_t = out_of_window
            queueinfo.queue_name = queue_name
            queueinfo.call_picker = ''
            self.session.add(queueinfo)
        self.session.commit()

    def test_get_received_call(self):
        window = 3600 # one hour
        count_in_window = 5
        queue_name = 'service'
        self._insert_received_calls(window, count_in_window, queue_name)
        number_of_received_calls = self._queue_statistic_dao.get_received_call_count('service', window)
        self.assertEqual(number_of_received_calls, count_in_window)



    def _insert_calls_answered_and_unanwered(self, window, nb_in_window, queue_name):
        out_of_window_delta = window + 30
        in_window = time.time()
        count_out_window = 3
        out_of_window = time.time() - out_of_window_delta
        for i in range(nb_in_window):
            queueinfo = QueueInfo()
            queueinfo.call_time_t = in_window
            queueinfo.queue_name = queue_name
            queueinfo.call_picker = 'pascal'
            self.session.add(queueinfo)
        for i in range(count_out_window):
            queueinfo = QueueInfo()
            queueinfo.call_time_t = out_of_window
            queueinfo.queue_name = queue_name
            queueinfo.call_picker = 'pascal'
            self.session.add(queueinfo)
        self.session.commit()

    def _insert_calls_abandonned(self, window, nb_in_window, queue_name):
        out_of_window_delta = window + 30
        in_window = time.time()
        count_out_window = 3
        out_of_window = time.time() - out_of_window_delta
        for i in range(nb_in_window):
            queueinfo = QueueInfo()
            queueinfo.call_time_t = in_window
            queueinfo.queue_name = queue_name
            queueinfo.hold_time = 5
            queueinfo.call_picker = None if i % 2 == 0 else ''
            self.session.add(queueinfo)
        for i in range(count_out_window):
            queueinfo = QueueInfo()
            queueinfo.call_time_t = out_of_window
            queueinfo.queue_name = queue_name
            queueinfo.hold_time = 5
            queueinfo.call_picker = ''
            self.session.add(queueinfo)
        self.session.commit()

    def _insert_ongoing_call(self, queue_name):
        queue_info = QueueInfo()
        queue_info.call_time_t = time.time() - 5
        queue_info.queue_name = queue_name
        queue_info.call_picker = ''
        queue_info.hold_time = None
        self.session.add(queue_info)
        self.session.commit()

    def test_get_answered_call(self):
        window = 3600 # one hour
        unanswered_in_window = 5
        answered_in_window = 7
        queue_name = 'service'
        self._insert_received_calls(window, unanswered_in_window, queue_name)
        self._insert_calls_answered_and_unanwered(window, answered_in_window, queue_name)

        number_of_answered_calls = self._queue_statistic_dao.get_answered_call_count(queue_name, window)

        self.assertEqual(answered_in_window, number_of_answered_calls)
        
    def test_get_abandonned_call(self):
        window = 3600 # one hour
        unanswered_in_window = 5
        answered_in_window = 7
        abandonned_calls = 9
        queue_name = 'service'
        self._insert_ongoing_call(queue_name)
        self._insert_calls_abandonned(window, abandonned_calls, queue_name)
        self._insert_received_calls(window, unanswered_in_window, queue_name)
        self._insert_calls_answered_and_unanwered(window, answered_in_window, queue_name)

        number_of_abandonned_calls = self._queue_statistic_dao.get_abandonned_call_count(queue_name, window)

        self.assertEqual(abandonned_calls, number_of_abandonned_calls)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()