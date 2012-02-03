# -*- coding: UTF-8 -*-

import unittest

from tests.mock import Mock
from xivo_cti.cti_command import Command
from xivo_cti.statistics.queuestatisticmanager import QueueStatisticManager
from xivo_cti.statistics.queuestatisticencoder import QueueStatisticEncoder
from xivo_cti.innerdata import Safe
from xivo_cti.lists.cti_queuelist import QueueList
from xivo_cti.ctiserver import CTIServer
from xivo_cti.services.user_service_manager import UserServiceManager


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
        self.user_service_manager = Mock(UserServiceManager)

    def _create_featureput_command(self, funct, user_id, value):
        command = {'class': "featuresput",
                   "commandid": 819690795,
                   "function": funct,
                   "value": value}
        cti_command = Command(self.conn, command)
        cti_command.user_service_manager = self.user_service_manager
        cti_command.ruserid = user_id
        return cti_command

    def test_features_put_enable_rna_fwd(self):
        user_id = 6789
        destination = '105'
        cti_command = self._create_featureput_command('fwd', user_id, {'destrna': destination,
                                                                       'enablerna': True})

        reply = cti_command.regcommand_featuresput()

        self.user_service_manager.enable_rna_fwd.assert_called_once_with(user_id, destination)
        self.assertEqual(reply, self.features_return_success)

    def test_features_put_disable_busy_fwd(self):
        user_id = 189
        destination = '123'
        cti_command = self._create_featureput_command('fwd', user_id, {'destbusy': destination,
                                                                       'enablebusy': False})

        reply = cti_command.regcommand_featuresput()

        self.user_service_manager.disable_busy_fwd.assert_called_once_with(user_id, destination)
        self.assertEqual(reply, self.features_return_success)

    def test_features_put_enable_busy_fwd(self):
        user_id = 679
        destination = '109'
        cti_command = self._create_featureput_command('fwd', user_id, {'destbusy': destination,
                                                                       'enablebusy': True})

        reply = cti_command.regcommand_featuresput()

        self.user_service_manager.enable_busy_fwd.assert_called_once_with(user_id, destination)
        self.assertEqual(reply, self.features_return_success)

    def test_features_put_disable_rna_fwd(self):
        user_id = 6789
        destination = '105'
        cti_command = self._create_featureput_command('fwd', user_id, {'destrna': destination,
                                                                       'enablerna': False})

        reply = cti_command.regcommand_featuresput()

        self.user_service_manager.disable_rna_fwd.assert_called_once_with(user_id, destination)
        self.assertEqual(reply, self.features_return_success)

    def test_features_put_enable_unconditional_fwd(self):
        user_id = 4567
        destination = '101'
        cti_command = self._create_featureput_command('fwd', user_id, {"destunc": destination,
                                                                       "enableunc": True})

        reply = cti_command.regcommand_featuresput()

        self.user_service_manager.enable_unconditional_fwd.assert_called_once_with(user_id, destination)
        self.assertEqual(reply, self.features_return_success)

    def test_features_put_disable_unconditional_fwd(self):
        user_id = 555
        destination = '101'
        cti_command = self._create_featureput_command('fwd', user_id, {'enableunc': False,
                                                                       'destunc': destination})

        reply = cti_command.regcommand_featuresput()

        self.user_service_manager.disable_unconditional_fwd.assert_called_once_with(user_id, destination)
        self.assertEqual(reply, self.features_return_success)

    def test_features_put_enable_filter(self):
        user_id = 14
        cti_command = self._create_featureput_command("incallfilter", user_id, True)

        reply = cti_command.regcommand_featuresput()

        self.user_service_manager.enable_filter.assert_called_once_with(user_id)
        self.assertEqual(reply, self.features_return_success)

    def test_features_put_disable_filter(self):
        user_id = 143
        cti_command = self._create_featureput_command("incallfilter", user_id, False)

        reply = cti_command.regcommand_featuresput()

        self.user_service_manager.disable_filter.assert_called_once_with(user_id)
        self.assertEqual(reply, self.features_return_success)

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
        queueStatistics = Mock(QueueStatisticManager)
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
