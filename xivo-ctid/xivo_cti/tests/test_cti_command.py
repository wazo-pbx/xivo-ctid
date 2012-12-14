# -*- coding: utf-8 -*-

import unittest

from mock import Mock, patch
from xivo_cti.cti_command import Command
from xivo_cti.statistics.queue_statistics_manager import QueueStatisticsManager
from xivo_cti.statistics.queue_statistics_encoder import QueueStatisticsEncoder
from xivo_cti.innerdata import Safe
from xivo_cti.ctiserver import CTIServer


class Test(unittest.TestCase):

    features_return_success = {'status': 'OK'}

    def setUp(self):
        self._ctiserver = Mock(CTIServer)
        self._innerdata = Mock(Safe)
        self.conn = Mock()
        self.conn.requester = ('test_requester', 1)
        self.conn._ctiserver = self._ctiserver
        self._ctiserver.safe = self._innerdata

    @patch('xivo_cti.ioc.context.context.get', Mock())
    def test_regcommand_getqueuesstats_no_result(self):
        message = {}
        cti_command = Command(self.conn, message)
        self.assertEqual(cti_command.regcommand_getqueuesstats(), {},
                         'Default return an empty dict')

    @patch('xivo_cti.dao.queue.get_name_from_id')
    @patch('xivo_cti.ioc.context.context.get', Mock())
    def test_regcommand_getqueuesstats_one_queue(self, mock_get_name_from_id):
        message = {"class": "getqueuesstats",
                   "commandid": 1234,
                   "on": {"3": {"window": "3600", "xqos": "60"}}}
        queueStatistics = Mock(QueueStatisticsManager)
        encoder = Mock(QueueStatisticsEncoder)
        cti_command = Command(self.conn, message)
        cti_command._queue_statistics_manager = queueStatistics
        cti_command._queue_statistics_encoder = encoder
        mock_get_name_from_id.return_value = 'service'

        queueStatistics.get_statistics.return_value = queueStatistics
        statisticsToEncode = {'3': queueStatistics}

        encoder.encode.return_value = {'return value': {'value1': 'first stat'}}

        reply = cti_command.regcommand_getqueuesstats()
        self.assertEqual(reply, {'return value': {'value1': 'first stat'}})

        queueStatistics.get_statistics.assert_called_with('service', 60, 3600)
        encoder.encode.assert_called_with(statisticsToEncode)
