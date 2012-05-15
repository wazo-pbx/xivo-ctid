# -*- coding: utf-8 -*-

import unittest

from tests.mock import Mock
from xivo_cti.cti_command import Command
from xivo_cti.statistics.queue_statistics_manager import QueueStatisticsManager
from xivo_cti.statistics.queuestatisticencoder import QueueStatisticEncoder
from xivo_cti.innerdata import Safe
from xivo_cti.lists.cti_queuelist import QueueList
from xivo_cti.ctiserver import CTIServer


class Test(unittest.TestCase):

    features_return_success = {'status': 'OK'}

    def setUp(self):
        self._ctiserver = Mock(CTIServer)
        self._ipbxid = 'my_ipbx_id'
        self._innerdata = Mock(Safe)
        self.conn = Mock()
        self.conn.requester = ('test_requester', 1)
        self.conn._ctiserver = self._ctiserver
        self._ctiserver.safe = {self._ipbxid: self._innerdata}

    def test_regcommand_getqueuesstats_no_result(self):
        message = {}
        cti_command = Command(self.conn, message)
        self.assertEqual(cti_command.regcommand_getqueuesstats(), {},
                         'Default return an empty dict')

    def test_regcommand_getqueuesstats_one_queue(self):
        queueList = Mock(QueueList)
        queueList.keeplist = {'3': {'name': 'service'}}
        safe = Mock(Safe)
        safe.xod_config = {'queues': queueList}

        message = {"class": "getqueuesstats",
                   "commandid": 1234,
                   "on": {"3": {"window": "3600", "xqos": "60"}}}
        queueStatistics = Mock(QueueStatisticsManager)
        encoder = Mock(QueueStatisticEncoder)
        cti_command = Command(self.conn, message)
        cti_command.innerdata = safe
        cti_command._queue_statistic_manager = queueStatistics
        cti_command._queue_statistic_encoder = encoder

        queueStatistics.get_statistics.return_value = queueStatistics
        statisticsToEncode = {'3': queueStatistics}

        encoder.encode.return_value = {'return value': {'value1': 'first stat'}}

        reply = cti_command.regcommand_getqueuesstats()
        self.assertEqual(reply, {'return value': {'value1': 'first stat'}})

        queueStatistics.get_statistics.assert_called_with('service', 60, 3600)
        encoder.encode.assert_called_with(statisticsToEncode)
