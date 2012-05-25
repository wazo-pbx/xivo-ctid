#!/usr/bin/python
# vim: set fileencoding=utf-8 :

# Copyright (C) 2007-2012  Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Pro-formatique SARL. See the LICENSE file at top of the
# source tree or delivered in the installable package in which XiVO CTI Server
# is distributed for more details.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import cjson
import logging
import os
import Queue
import select
import signal
import socket
import ssl
import sys
import time
import threading
import urllib

from xivo import daemonize

from xivo_cti import amiinterpret
from xivo_cti import cti_config
from xivo_cti import innerdata
from xivo_cti.client_connection import ClientConnection
from xivo_cti.dao.alchemy import dbconnection
from xivo_cti.queue_logger import QueueLogger
from xivo_cti.interfaces import interface_ami
from xivo_cti.interfaces import interface_info
from xivo_cti.interfaces import interface_webi
from xivo_cti.interfaces import interface_cti
from xivo_cti.interfaces import interface_fagi
from xivo_cti.interfaces.interfaces import DisconnectCause
from xivo_cti.dao.userfeaturesdao import UserFeaturesDAO
from xivo_cti.services.user_service_notifier import UserServiceNotifier
from xivo_cti.services.user_service_manager import UserServiceManager
from xivo_cti.cti.commands.user_service.enable_dnd import EnableDND
from xivo_cti.cti.commands.user_service.disable_dnd import DisableDND
from xivo_cti.cti.commands.user_service.enable_filter import EnableFilter
from xivo_cti.cti.commands.user_service.disable_filter import DisableFilter
from xivo_cti.cti.commands.user_service.enable_unconditional_forward import EnableUnconditionalForward
from xivo_cti.cti.commands.user_service.disable_unconditional_forward import DisableUnconditionalForward
from xivo_cti.cti.commands.user_service.enable_noanswer_forward import EnableNoAnswerForward
from xivo_cti.cti.commands.user_service.disable_noanswer_forward import DisableNoAnswerForward
from xivo_cti.cti.commands.user_service.enable_busy_forward import EnableBusyForward
from xivo_cti.cti.commands.user_service.disable_busy_forward import DisableBusyForward
from xivo_cti.cti.commands.subscribe_queue_entry_update import SubscribeQueueEntryUpdate
from xivo_cti.funckey.funckey_manager import FunckeyManager
from xivo_cti.dao.extensionsdao import ExtensionsDAO
from xivo_cti.dao.phonefunckeydao import PhoneFunckeyDAO
from xivo_cti.dao.agentfeaturesdao import AgentFeaturesDAO
from xivo_cti.services.agent_service_manager import AgentServiceManager
from xivo_cti.services.agent_executor import AgentExecutor
from xivo_cti.cti.commands.agent_login import AgentLogin
from xivo_cti.dao.linefeaturesdao import LineFeaturesDAO
from xivo_cti.dao.meetmefeaturesdao import MeetmeFeaturesDAO
from xivo_cti.services.queue_service_manager import QueueServiceManager
from xivo_cti.services.queuemember_service_manager import QueueMemberServiceManager
from xivo_cti.dao.queuememberdao import QueueMemberDAO
from xivo_cti.dao.innerdatadao import InnerdataDAO
from xivo_cti.tools.delta_computer import DeltaComputer
from xivo_cti.services.queuemember_service_notifier import QueueMemberServiceNotifier
from sqlalchemy.exc import OperationalError
from xivo_cti.statistics.statistics_producer_initializer import StatisticsProducerInitializer
from xivo_cti.statistics.queue_statistics_producer import QueueStatisticsProducer
from xivo_cti.statistics.statistics_notifier import StatisticsNotifier
from xivo_cti.statistics.queue_statistics_manager import QueueStatisticsManager
from xivo_cti.cti.commands.subscribetoqueuesstats import SubscribeToQueuesStats
from xivo_cti.services.presence_service_executor import PresenceServiceExecutor
from xivo_cti.services.presence_service_manager import PresenceServiceManager

from xivo_cti.services.queue_entry_manager import QueueEntryManager

from xivo_cti.services.queue_entry_notifier import QueueEntryNotifier
from xivo_cti.services.queue_entry_encoder import QueueEntryEncoder
from xivo_cti.dao.queue_features_dao import QueueFeaturesDAO
from xivo_cti.services import queue_entry_manager
from xivo_cti.statistics import queue_statistics_manager
from xivo_cti.statistics import queue_statistics_producer
from xivo_cti.cti.commands.logout import Logout
from xivo_cti.cti.commands.queue_unpause import QueueUnPause
from xivo_cti.cti.commands.queue_pause import QueuePause
from xivo_cti.cti.commands.queue_add import QueueAdd
from xivo_cti.cti.commands.queue_remove import QueueRemove


logger = logging.getLogger('main')


class CTIServer(object):

    xivoversion = '1.2'
    revision = 'githash'
    xdname = 'XiVO CTI Server'

    def __init__(self):
        self.nreload = 0
        self.myami = {}
        self.mycti = {}
        self.safe = {}
        self.timeout_queue = None
        self.pipe_queued_threads = None
        self._config = None
        self._user_service_manager = None

    def _set_signal_handlers(self):
        signal.signal(signal.SIGINT, self.sighandler)
        signal.signal(signal.SIGTERM, self.sighandler)
        signal.signal(signal.SIGHUP, self.sighandler_reload)

    def _set_logger(self):
        logging.basicConfig(level=logging.INFO)
        try:
            logfilehandler = logging.FileHandler(cti_config.LOGFILENAME)
            formatter = logging.Formatter(
                '%%(asctime)s %s[%%(process)d] (%%(levelname)s) (%%(name)s): %%(message)s'
                % cti_config.DAEMONNAME)
            logfilehandler.setFormatter(formatter)
            root_logger = logging.getLogger()
            root_logger.addHandler(logfilehandler)
            if cti_config.DEBUG_MODE:
                root_logger.setLevel(logging.DEBUG)
        except Exception:
            logger.exception('logfilehandler')

    def _daemonize(self):
        if not cti_config.DEBUG_MODE:
            daemonize.daemonize()
        daemonize.lock_pidfile_or_die(cti_config.PIDFILE)

    def setup(self):
        self._set_logger()
        self._daemonize()
        self._config = cti_config.Config.get_instance()
        self._config.update()
        self.timeout_queue = Queue.Queue()
        self._set_signal_handlers()
        self._init_db_connection_pool()
        self._init_queue_stats()

        self._user_service_manager = UserServiceManager()
        self._user_service_notifier = UserServiceNotifier()
        self._funckey_manager = FunckeyManager()
        self._agent_service_manager = AgentServiceManager()
        self._agent_executor = AgentExecutor()
        self._presence_service_manager = PresenceServiceManager()
        self._presence_service_executor = PresenceServiceExecutor()
        self._statistics_notifier = StatisticsNotifier()
        self._queue_service_manager = QueueServiceManager.get_instance()
        self._queue_statistics_producer = QueueStatisticsProducer.get_instance()
        self._queuemember_service_manager = QueueMemberServiceManager()
        self._queuemember_service_notifier = QueueMemberServiceNotifier.get_instance()

        self._innerdata_dao = InnerdataDAO()
        self._user_features_dao = UserFeaturesDAO.new_from_uri('queue_stats')
        self._extensions_dao = ExtensionsDAO.new_from_uri('queue_stats')
        self._phone_funckey_dao = PhoneFunckeyDAO.new_from_uri('queue_stats')
        self._agent_features_dao = AgentFeaturesDAO.new_from_uri('queue_stats')
        self._line_features_dao = LineFeaturesDAO.new_from_uri('queue_stats')
        self._queue_features_dao = QueueFeaturesDAO.new_from_uri('queue_stats')
        self._meetme_features_dao = MeetmeFeaturesDAO.new_from_uri('queue_stats')

        self._funckey_manager.extensionsdao = self._extensions_dao
        self._funckey_manager.phone_funckey_dao = self._phone_funckey_dao

        self._presence_service_executor.user_features_dao = self._user_features_dao
        self._presence_service_executor.user_service_manager = self._user_service_manager
        self._presence_service_executor.agent_service_manager = self._agent_service_manager

        self._presence_service_manager.innerdata_dao = self._innerdata_dao

        self._user_service_manager.user_features_dao = self._user_features_dao
        self._user_service_manager.phone_funckey_dao = self._phone_funckey_dao
        self._user_service_manager.user_service_notifier = self._user_service_notifier
        self._user_service_manager.line_features_dao = self._line_features_dao
        self._user_service_manager.presence_service_manager = self._presence_service_manager
        self._user_service_manager.presence_service_executor = self._presence_service_executor
        self._user_service_manager.agent_service_manager = self._agent_service_manager
        self._user_service_manager.funckey_manager = self._funckey_manager

        self._agent_service_manager.line_features_dao = self._line_features_dao
        self._agent_service_manager.agent_features_dao = self._agent_features_dao
        self._agent_service_manager.user_features_dao = self._user_features_dao
        self._agent_service_manager.agent_executor = self._agent_executor
        self._queue_service_manager.innerdata_dao = self._innerdata_dao

        self._queue_entry_manager = QueueEntryManager.get_instance()
        self._queue_statistic_manager = QueueStatisticsManager.get_instance()
        self._queue_entry_notifier = QueueEntryNotifier.get_instance()
        self._queue_entry_encoder = QueueEntryEncoder.get_instance()

        self._queue_entry_manager._notifier = self._queue_entry_notifier
        self._queue_entry_manager._encoder = self._queue_entry_encoder
        self._queue_entry_manager._queue_features_dao = self._queue_features_dao
        self._queue_entry_manager._statistics_notifier = self._statistics_notifier
        self._queue_entry_encoder.queue_features_dao = self._queue_features_dao
        self._queue_entry_notifier.queue_features_dao = self._queue_features_dao

        self._queuemember_service_manager.queuemember_dao = QueueMemberDAO.new_from_uri('queue_stats')
        self._queuemember_service_manager.innerdata_dao = self._innerdata_dao
        self._queuemember_service_manager.queue_features_dao = self._queue_features_dao
        self._queuemember_service_manager.agent_service_manager = self._agent_service_manager
        self._queuemember_service_manager.delta_computer = DeltaComputer()
        self._queuemember_service_manager.queuemember_notifier = self._queuemember_service_notifier
        self._queuemember_service_notifier.innerdata_dao = self._queuemember_service_manager.innerdata_dao

        self._statistics_producer_initializer = StatisticsProducerInitializer(self._queue_service_manager)

        self._queue_statistics_producer.notifier = self._statistics_notifier

        queue_entry_manager.register_events()
        queue_statistics_manager.register_events()
        queue_statistics_producer.register_events()

        self._register_cti_callbacks()

    def _register_cti_callbacks(self):
        EnableDND.register_callback_params(self._user_service_manager.enable_dnd, ['user_id'])
        DisableDND.register_callback_params(self._user_service_manager.disable_dnd, ['user_id'])
        EnableFilter.register_callback_params(self._user_service_manager.enable_filter, ['user_id'])
        DisableFilter.register_callback_params(self._user_service_manager.disable_filter, ['user_id'])
        EnableUnconditionalForward.register_callback_params(self._user_service_manager.enable_unconditional_fwd, ['user_id', 'destination'])
        DisableUnconditionalForward.register_callback_params(self._user_service_manager.disable_unconditional_fwd, ['user_id', 'destination'])
        EnableNoAnswerForward.register_callback_params(self._user_service_manager.enable_rna_fwd, ['user_id', 'destination'])
        DisableNoAnswerForward.register_callback_params(self._user_service_manager.disable_rna_fwd, ['user_id', 'destination'])
        EnableBusyForward.register_callback_params(self._user_service_manager.enable_busy_fwd, ['user_id', 'destination'])
        DisableBusyForward.register_callback_params(self._user_service_manager.disable_busy_fwd, ['user_id', 'destination'])

        SubscribeToQueuesStats.register_callback_params(self._statistics_notifier.subscribe, ['cti_connection'])
        SubscribeToQueuesStats.register_callback_params(self._queue_statistics_producer.send_all_stats, ['cti_connection'])
        SubscribeToQueuesStats.register_callback_params(self._queue_statistic_manager.get_all_queue_summary)
        SubscribeToQueuesStats.register_callback_params(self._queue_entry_manager.publish_all_longest_wait_time, ['cti_connection'])
        SubscribeQueueEntryUpdate.register_callback_params(
            self._queue_entry_notifier.subscribe, ['cti_connection', 'queue_id'])

        AgentLogin.register_callback_params(self._agent_service_manager.log_agent,
                                            ['user_id', 'agent_id', 'agent_phone_number'])

        Logout.register_callback_params(self._user_service_manager.disconnect, ['user_id'])

        QueueUnPause.register_callback_params(
            self._queuemember_service_manager.dispach_command, ['command', 'member', 'queue', 'dopause'])
        QueuePause.register_callback_params(
            self._queuemember_service_manager.dispach_command, ['command', 'member', 'queue', 'dopause'])
        QueueAdd.register_callback_params(
            self._queuemember_service_manager.dispach_command, ['command', 'member', 'queue'])
        QueueRemove.register_callback_params(
            self._queuemember_service_manager.dispach_command, ['command', 'member', 'queue'])

    def _init_statistics_producers(self):
        self._statistics_producer_initializer.init_queue_statistics_producer(self._queue_statistics_producer)
        self._queuemember_service_notifier.queue_statistics_producer = self._queue_statistics_producer

    def run(self):
        while True:
            try:
                self.main_loop()
            except Exception:
                logger.exception('main loop has crashed ... retrying in 5 seconds ...')
                time.sleep(5)

    ## \brief Handler for catching signals (in the main thread)
    def sighandler(self, signum, frame):
        logger.warning('(sighandler) signal %s lineno %s (atq = %s) received : quits',
                       signum, frame.f_lineno, self.askedtoquit)
        for t in filter(lambda x: x.getName() != 'MainThread', threading.enumerate()):
            print '--- living thread <%s>' % (t.getName())
            t._Thread__stop()
        self.askedtoquit = True

    ## \brief Handler for catching signals (in the main thread)
    def sighandler_reload(self, signum, frame):
        logger.warning('(sighandler_reload) signal %s lineno %s (atq = %s) received : reloads',
                       signum, frame.f_lineno, self.askedtoquit)
        self.askedtoquit = False

    def manage_tcp_connections(self, sel_i, msg, kind):
        """
        Dispatches the message's handling according to the connection's kind.
        """
        closemenow = False
        if not isinstance(kind, str):   # CTI, INFO, WEBI
            replies = kind.manage_connection(msg)
            for reply in replies:
                if reply:
                    if 'closemenow' in reply:
                        closemenow = reply.get('closemenow')
                    if 'message' in reply:
                        if reply.get('dest'):
                            self.send_to_cti_client(reply.get('dest'),
                                                    reply.get('message'))
                        else:
                            kind.reply(reply.get('message'))
                    elif 'warning' in reply:
                        kind.reply(reply.get('warning'))
        else:
            logger.warning('unknown connection kind %s', kind)
        return closemenow

    def find_matching_ipbxid(self, ipaddress):
        found_ipbxid = None
        for ipbxid, ipbxconfig in self._config.getconfig('ipbxes').iteritems():
            if 'ipbx_connection' in ipbxconfig:
                connparams = ipbxconfig.get('ipbx_connection')
                cfg_ip_address = connparams.get('ipaddress')
                if ipaddress == socket.gethostbyname(cfg_ip_address):
                    found_ipbxid = ipbxid
                    break
        return found_ipbxid

    def checkqueue(self):
        ncount = 0
        while self.timeout_queue.qsize() > 0:
            ncount += 1
            (toload,) = self.timeout_queue.get()
            action = toload.get('action')
            if action == 'ipbxup':
                sockparams = toload.get('properties').get('sockparams')
                data = toload.get('properties').get('data')
                if data.startswith('asterisk'):
                    got_ip_address = sockparams[0]
                    ipbxid = self.find_matching_ipbxid(got_ip_address)
                    if ipbxid:
                        if not self.myami[ipbxid].connected():
                            logger.info('attempt to reconnect to the AMI for %s', ipbxid)
                            z = self.myami[ipbxid].connect()
                            if z:
                                self.fdlist_ami[z] = self.myami[ipbxid]
                    else:
                        logger.warning('did not found a matching ipbxid for the address %s',
                                       got_ip_address)
            elif action == 'ctilogin':
                connc = toload.get('properties')
                connc.close()
                if connc in self.fdlist_established:
                    del self.fdlist_established[connc]
            else:
                logger.warning('checkqueue : unknown action received : %s', action)
        return ncount

    def cb_timer(self, *args):
        try:
            tname = threading.currentThread()
            tname.setName('Thread-main')
            self.timeout_queue.put(args)
            os.write(self.pipe_queued_threads[1], 'main:\n')
        except Exception:
            logger.exception('cb_timer %s', args)

    def updates_period(self):
        return int(self._config.getconfig('main').get('updates_period', '3600'))

    def _init_db_connection_pool(self):
        # XXX we should probably close the db_connection_pool when main loop exit
        dbconnection.unregister_db_connection_pool()
        dbconnection.register_db_connection_pool(self._new_db_connection_pool())

    def _new_db_connection_pool(self):
        return dbconnection.DBConnectionPool(dbconnection.DBConnection)

    def _init_queue_stats(self):
        queue_stats_uri = self._config.getconfig('main')['asterisk_queuestat_db']
        QueueLogger.init(queue_stats_uri)
        dbconnection.add_connection_as(queue_stats_uri, 'queue_stats')

    def main_loop(self):
        self.askedtoquit = False

        self.time_start = time.localtime()
        logger.info('# STARTING XiVO CTI Server %s (pid %d) / git:%s # (0/3) Starting (%d)',
                    self.xivoversion, os.getpid(), self.revision, self.nreload)
        self.nreload += 1

        self.update_userlist = {}
        self.lastrequest_time = {}

        self._config.set_ipwebs(cti_config.XIVOIP)
        if cti_config.XIVO_CONF_OVER:
            urldata = urllib.urlopen(cti_config.XIVO_CONF_OVER)
            payload = urldata.read()
            urldata.close()
            overconf = cjson.decode(payload)
        self._config.update()

        xivoconf_general = self._config.getconfig('main')

        # loads the general configuration
        socktimeout = float(xivoconf_general.get('sockettimeout', '2'))
        self._config.set_parting_options(xivoconf_general.get('parting_astid_context'))

        socket.setdefaulttimeout(socktimeout)

        if not self.pipe_queued_threads:
            self.pipe_queued_threads = os.pipe()

        # sockets management
        self.fdlist_established = {}
        self.fdlist_listen_cti = {}
        self.fdlist_udp_cti = {}
        self.fdlist_ami = {}

        logger.info("the monitored ipbx's is/are : %s", self._config.getconfig('ipbxes').keys())

        for ipbxid, ipbxconfig in self._config.getconfig('ipbxes').iteritems():
            if 'ipbx_connection' in ipbxconfig:
                self.myipbxid = ipbxid
                break
        else:
            self.myipbxid = None

        logger.info('# STARTING %s # (1/2) Local AMI socket connection', self.xdname)
        if self.myipbxid:
            ipbxconfig = self._config.getconfig('ipbxes').get(self.myipbxid)
            safe = innerdata.Safe(self, self.myipbxid, ipbxconfig.get('urllists'))
            self.safe[self.myipbxid] = safe
            safe.user_service_manager = self._user_service_manager
            safe.user_features_dao = self._user_features_dao
            self._user_features_dao._innerdata = safe
            self._user_service_notifier.events_cti = safe.events_cti
            self._user_service_notifier.ipbx_id = self.myipbxid
            self._queuemember_service_manager.innerdata_dao.innerdata = safe
            self._queuemember_service_notifier.events_cti = safe.events_cti
            self._queuemember_service_notifier.ipbx_id = self.myipbxid
            self._user_service_manager.presence_service_executor._innerdata = safe
            self.safe[self.myipbxid].register_cti_handlers()
            self.safe[self.myipbxid].register_ami_handlers()
            self.safe[self.myipbxid].update_directories()
            self.myami[self.myipbxid] = interface_ami.AMI(self, self.myipbxid)
            self.commandclass = amiinterpret.AMI_1_8(self, self.myipbxid)
            self.commandclass.user_features_dao = self._user_features_dao
            self.commandclass.queuemember_service_manager = self._queuemember_service_manager
            self._queuemember_service_notifier.interface_ami = self.myami[self.myipbxid]
            self._queue_entry_manager._ami = self.myami[self.myipbxid]

            logger.info('# STARTING %s / git:%s / %d',
                        self.xdname, self.safe[self.myipbxid].version(), self.nreload)

            self.update_userlist[self.myipbxid] = []
            self.lastrequest_time[self.myipbxid] = time.time()

            z = self.myami[self.myipbxid].connect()
            if z:
                self.fdlist_ami[z] = self.myami[self.myipbxid]
                self._funckey_manager.ami = self.myami[self.myipbxid].amicl
                self._agent_service_manager.agent_executor.ami = self.myami[self.myipbxid].amicl
                self._queue_statistic_manager.ami_wrapper = self.myami[self.myipbxid].amicl

            try:
                self.safe[self.myipbxid].update_config_list_all()
            except Exception:
                logger.exception('%s : commandclass.updates()', self.myipbxid)
            self._queuemember_service_manager.update_config()
            self._init_statistics_producers()

        logger.info('# STARTING %s # (2/2) listening sockets (CTI, WEBI, FAGI, INFO)', self.xdname)
        # opens the listening socket for incoming (CTI, WEBI, FAGI, INFO) connections
        for kind, bind_and_port in xivoconf_general.get('incoming_tcp', {}).iteritems():
            allow_kind = True
            if len(bind_and_port) > 2:
                allow_kind = bind_and_port[2]
            if not allow_kind:
                logger.warning('%s kind listening socket has been explicitly disabled', kind)
                continue
            try:
                (bind, port) = bind_and_port[:2]
                trueport = int(port) + cti_config.PORTDELTA
                gai = socket.getaddrinfo(bind, trueport, 0, socket.SOCK_STREAM, socket.SOL_TCP)
                if not gai:
                    continue
                (afinet, socktype, proto, dummy, bindtuple) = gai[0]
                UIsock = socket.socket(afinet, socktype)
                UIsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                UIsock.bind(bindtuple)
                UIsock.listen(10)
                self.fdlist_listen_cti[UIsock] = '%s:%s' % (kind, 1)
            except Exception:
                logger.exception('tcp %s %d', bind, trueport)

        for kind, bind_and_port in xivoconf_general.get('incoming_udp', {}).iteritems():
            allow_kind = True
            if len(bind_and_port) > 2:
                allow_kind = bind_and_port[2]
            if not allow_kind:
                logger.warning('%s kind listening socket has been explicitly disabled', kind)
                continue
            try:
                (bind, port) = bind_and_port[:2]
                trueport = int(port) + cti_config.PORTDELTA
                gai = socket.getaddrinfo(bind, trueport, 0, socket.SOCK_DGRAM, socket.SOL_UDP)
                if not gai:
                    continue
                (afinet, socktype, proto, dummy, bindtuple) = gai[0]
                UIsock = socket.socket(afinet, socktype)
                UIsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                UIsock.bind(bindtuple)
                self.fdlist_udp_cti[UIsock] = '%s:%s' % (kind, 1)
            except Exception:
                logger.exception('udp %s %d', bind, trueport)

        # Main select() loop - Receive messages
        if not self._config.getconfig():
            nsecs = 5
            logger.info('waiting %d seconds in case a config would be available ...', nsecs)
            try:
                time.sleep(nsecs)
                # select.select([], [], [], nsecs)
            except:
                sys.exit()
        else:
            while not self.askedtoquit:
                self.select_step()

    def get_connected(self, tomatch):
        clist = list()
        for k in self.fdlist_established.itervalues():
            if not isinstance(k, str) and k.kind in ['CTI', 'CTIS']:
                ipbxid = k.connection_details.get('ipbxid')
                userid = k.connection_details.get('userid')
                if self.safe.get(ipbxid).user_match(userid, tomatch):
                    clist.append(k)
        return clist

    def sendsheettolist(self, tsl, payload):
        for k in tsl:
            k.reply(payload)

    def loop_over_cti_queues(self):
        for ipbxid, innerdata in self.safe.iteritems():
            self.loop_over_cti_queue(innerdata)

    def loop_over_cti_queue(self, innerdata):
        cti_queue = innerdata.events_cti
        while cti_queue.qsize() > 0:
            it = cti_queue.get()
            for k in self.fdlist_established.itervalues():
                if not isinstance(k, str) and k.kind in ['CTI', 'CTIS']:
                    k.append_msg(it)

    def set_transfer_socket(self, faxobj, direction):
        for iconn, kind in self.fdlist_established.iteritems():
            if kind.kind in ['CTI', 'CTIS']:
                peername = '%s:%d' % iconn.getpeername()
                if peername == faxobj.socketref:
                    kind.set_as_transfer(direction, faxobj)
                    if direction == 's2c':
                        sendbuffer = ''
                        kind.reply(sendbuffer)
                    break

    def send_to_cti_client(self, who, what):
        (ipbxid, userid) = who.split('/')
        for k in self.fdlist_established.itervalues():
            if not isinstance(k, str) and k.kind in ['CTI', 'CTIS']:
                if ipbxid == self.myipbxid:
                    if k.connection_details.get('userid') == userid:
                        k.reply(what)
                else:
                    if k.connection_details.get('userid')[3:] == ipbxid:
                        k.reply(what)

    def select_step(self):
        try:
            fdtodel = []
            for cn in self.fdlist_established.keys():
                if isinstance(cn, ClientConnection):
                    if cn.isClosed and cn not in fdtodel:
                        fdtodel.append(cn)
                    if cn.toClose and not cn.need_sending():
                        cn.close()
                        if cn not in fdtodel:
                            fdtodel.append(cn)
            if fdtodel:
                for cn in fdtodel:
                    del self.fdlist_established[cn]

            self.fdlist_full = list()
            self.fdlist_full.append(self.pipe_queued_threads[0])
            self.fdlist_full.extend(self.fdlist_ami.keys())
            self.fdlist_full.extend(self.fdlist_listen_cti.keys())
            self.fdlist_full.extend(self.fdlist_udp_cti.keys())
            self.fdlist_full.extend(self.fdlist_established.keys())
            writefds = []
            for iconn, kind in self.fdlist_established.iteritems():
                if kind.kind in ['CTI', 'CTIS'] and iconn.need_sending():
                    writefds.append(iconn)
            [sels_i, sels_o, sels_e] = select.select(self.fdlist_full, writefds, [],
                                                     self.updates_period())

        except Exception:
            logger.exception('(select) probably Ctrl-C or daemon stop or daemon restart ...')
            logger.warning('(select) self.askedtoquit=%s fdlist_full=%s',
                           self.askedtoquit, self.fdlist_full)
            logger.warning('(select) current open TCP connections : (CTI, WEBI, FAGI, INFO) %s',
                           self.fdlist_established)
            logger.warning('(select) current open TCP connections : (AMI) %s',
                           self.fdlist_ami.keys())

            for s in self.fdlist_full:
                if s in self.fdlist_established:
                    if self.askedtoquit:
                        self.fdlist_established[s].disconnected(DisconnectCause.by_server_stop)
                    else:
                        self.fdlist_established[s].disconnected(DisconnectCause.by_server_reload)
                if not isinstance(s, int):
                    # the only one 'int' is the (read) pipe : no need to close/reopen it
                    s.close()

            if self.askedtoquit:
                time_uptime = int(time.time() - time.mktime(self.time_start))
                logger.info('# STOPPING XiVO CTI Server %s (pid %d) / git:%s # uptime %d s (since %s)',
                            self.xivoversion, os.getpid(), self.revision,
                            time_uptime, time.asctime(self.time_start))
                for t in filter(lambda x: x.getName() != 'MainThread', threading.enumerate()):
                    print '--- (stop) killing thread <%s>' % t.getName()
                    t._Thread__stop()
                daemonize.unlock_pidfile(cti_config.PIDFILE)
                sys.exit(5)
            else:
                # self.commandclass.reset('reload')
                self.askedtoquit = True
                for t in filter(lambda x: x.getName() != 'MainThread', threading.enumerate()):
                    print '--- (reload) the thread <%s> remains' % t.getName()
                    # t._Thread__stop() # does not work in reload case (vs. stop case)
                return

        try:

            # connexions ready for sending(writing)
            if sels_o:
                for sel_o in sels_o:
                    try:
                        sel_o.process_sending()
                    except ClientConnection.CloseException, cexc:
                        if sel_o in self.fdlist_established:
                            kind = self.fdlist_established[sel_o]
                            kind.disconnected(DisconnectCause.broken_pipe)
                            sel_o.close()
                            del self.fdlist_established[sel_o]

            if sels_i:
                for sel_i in sels_i:
                    # these AMI connections are used in order to manage AMI commands and events
                    if sel_i in self.fdlist_ami.keys():
                        try:
                            amiint = self.fdlist_ami.get(sel_i)
                            ipbxid = amiint.ipbxid
                            buf = sel_i.recv(cti_config.BUFSIZE_LARGE)
                            if len(buf) == 0:
                                logger.warning('AMI %s : CLOSING (%s)', ipbxid, time.asctime())
                                del self.fdlist_ami[sel_i]
                                sel_i.close()
                                amiint.disconnect()
                            else:
                                try:
                                    amiint.handle_event(buf)
                                except Exception:
                                    logger.exception('(handle_event) %s', ipbxid)
                        except Exception:
                            logger.exception('(amilist)')
                    elif sel_i in self.fdlist_udp_cti:
                        [kind, nmax] = self.fdlist_udp_cti[sel_i].split(':')
                        if kind == 'ANNOUNCE':
                            [data, sockparams] = sel_i.recvfrom(cti_config.BUFSIZE_LARGE)
                            # scheduling AMI reconnection
                            k = threading.Timer(1, self.cb_timer,
                                                ({'action': 'ipbxup',
                                                  'properties': {'data': data,
                                                                 'sockparams': sockparams}},))
                            k.setName('Thread-ipbxup-%s' % data.strip())
                            k.start()
                        else:
                            logger.warning('unknown kind %s received', kind)

                    # } the new TCP connections (CTI, WEBI, FAGI, INFO) are catched here
                    elif sel_i in self.fdlist_listen_cti:
                        [kind, nmax] = self.fdlist_listen_cti[sel_i].split(':')
                        [connc, sockparams] = sel_i.accept()
                        ctiseparator = '\n'
                        if kind == 'CTI':
                            connc = ClientConnection(connc, sockparams, ctiseparator)
                        elif kind == 'CTIS':
                            try:
                                connstream = ssl.wrap_socket(connc,
                                                             server_side=True,
                                                             certfile=self._config.getconfig('certfile'),
                                                             keyfile=self._config.getconfig('keyfile'),
                                                             ssl_version=cti_config.SSLPROTO)
                                connc = ClientConnection(connstream, sockparams, ctiseparator)
                            except ssl.SSLError:
                                logger.exception('%s:%s:%d cert=%s key=%s)',
                                                 kind, sockparams[0], sockparams[1],
                                                 self._config.getconfig('certfile'),
                                                 self._config.getconfig('keyfile'))
                                connc.close()
                                connc = None
                        # appending the opened socket to the ones watched
                        # connc.setblocking(0)
                        # connc.settimeout(2)
                        if connc:
                            if kind == 'INFO':
                                nc = interface_info.INFO(self)
                            elif kind == 'WEBI':
                                nc = interface_webi.WEBI(self)
                                nc.queuemember_service_manager = self._queuemember_service_manager
                            elif kind in ['CTI', 'CTIS']:
                                nc = getattr(interface_cti, kind)(self)
                                nc.user_service_manager = self._user_service_manager
                            elif kind == 'FAGI':
                                nc = interface_fagi.FAGI(self)

                            nc.connected(connc)
                            if kind in ['WEBI', 'FAGI', 'INFO']:
                                ipbxid = self.find_matching_ipbxid(sockparams[0])
                                ipbxid = self.myipbxid
                                if ipbxid:
                                    nc.set_ipbxid(ipbxid)
                                else:
                                    logger.warning('(%s interface) did not find a matching ipbxid for %s',
                                                   kind, sockparams[0])

                            if kind in ['CTI', 'CTIS']:
                                logintimeout = int(self._config.getconfig('main').get('logintimeout', 5))
                                # logintimeout = 3600
                                nc.logintimer = threading.Timer(logintimeout, self.cb_timer,
                                                                ({'action': 'ctilogin',
                                                                  'properties': connc},))
                                nc.logintimer.start()
                            self.fdlist_established[connc] = nc
                        else:
                            logger.warning('connc is not defined ...')

                    # } incoming TCP connections (CTI, WEBI, AGI, INFO)
                    elif sel_i in self.fdlist_established:
                        try:
                            kind = self.fdlist_established[sel_i]
                            requester = '%s:%d' % sel_i.getpeername()[:2]
                            closemenow = False
                            if isinstance(sel_i, ClientConnection):
                                try:
                                    lines = sel_i.readlines()
                                    for line in lines:
                                        if line:
                                            # XXX closemenow always take the latest value of the handled line, which
                                            #     might not be what we want (we want it to be True if it's been true
                                            #1    at least once)
                                            closemenow = self.manage_tcp_connections(sel_i, line, kind)
                                except ClientConnection.CloseException, cexc:
                                    kind.disconnected(DisconnectCause.broken_pipe)
                                    # don't close since it has been done
                                    del self.fdlist_established[sel_i]
                            else:
                                try:
                                    msg = sel_i.recv(cti_config.BUFSIZE_LARGE, socket.MSG_DONTWAIT)
                                    lmsg = len(msg)
                                except Exception:
                                    logger.exception('connection to %s (%s)', requester, kind)
                                    lmsg = 0

                                if lmsg > 0:
                                    try:
                                        closemenow = self.manage_tcp_connections(sel_i, msg, kind)
                                    except Exception:
                                        logger.exception('handling %s (%s)', requester, kind)
                                else:
                                    closemenow = True

                            if closemenow:
                                kind.disconnected(DisconnectCause.by_client)
                                sel_i.close()
                                del self.fdlist_established[sel_i]
                        except OperationalError:
                            logger.warning('Postgresql has been stopped, stopping...')
                            sys.exit(1)
                        except Exception:
                            # socket.error : exc.args[0]
                            logger.exception('[%s] %s', kind, sel_i)
                            try:
                                logger.warning('unexpected socket breakup')
                                kind.disconnected(DisconnectCause.broken_pipe)
                                sel_i.close()
                                del self.fdlist_established[sel_i]
                            except Exception:
                                logger.exception('[%s] (2nd exception)', kind)

                    # local pipe fd
                    elif self.pipe_queued_threads[0] == sel_i:
                        try:
                            pipebuf = os.read(sel_i, 1024)
                            if len(pipebuf) == 0:
                                logger.warning('pipe_queued_threads has been closed')
                            else:
                                for pb in pipebuf.split('\n'):
                                    if not pb:
                                        continue
                                    [kind, where] = pb.split(':')
                                    if kind in ['main', 'innerdata', 'ami']:
                                        if kind == 'main':
                                            nactions = self.checkqueue()
                                        elif kind == 'innerdata':
                                            nactions = self.safe[where].checkqueue()
                                        elif kind == 'ami':
                                            nactions = self.myami[where].checkqueue()
                                    else:
                                        logger.warning('unknown kind for %s', pb)
                        except Exception:
                            logger.exception('[pipe_queued_threads]')

                    self.loop_over_cti_queues()

                    for ipbxid, safe in self.safe.iteritems():
                        if ipbxid == self.myipbxid:
                            if self.update_userlist[ipbxid]:
                                self.lastrequest_time[ipbxid] = time.time()
                                logger.info('[%s] %s : updates (computed timeout) %s (%s)',
                                            self.xdname, ipbxid, time.asctime(), self.update_userlist[ipbxid])
                                try:
                                    # manage_connection.update_amisocks(ipbxid, self)
                                    self._config.update()
                                    safe.regular_update()
                                except Exception:
                                    logger.exception('%s : failed while updating lists and sockets (computed timeout)',
                                                     ipbxid)
                                try:
                                    if self.update_userlist[ipbxid]:
                                        while self.update_userlist[ipbxid]:
                                            tmp_ltr = self.update_userlist[ipbxid].pop()
                                            if tmp_ltr != 'xivo[cticonfig,update]':
                                                listtorequest = tmp_ltr[5:-12] + 's'
                                                safe.update_config_list(listtorequest)
                                                self.loop_over_cti_queues()
                                    else:
                                        safe.update_config_list_all()
                                        self.loop_over_cti_queues()
                                except Exception:
                                    logger.exception('%s : commandclass.updates() (computed timeout)', ipbxid)

            if not sels_i and not sels_o and not sels_e:
                # when nothing happens on the sockets, we fall here
                for ipbxid, safe in self.safe.iteritems():
                    if ipbxid == self.myipbxid:
                        try:
                            safe.update_config_list_all()
                        except Exception:
                            logger.exception('%s : commandclass.updates() (select timeout)', ipbxid)

                        self.lastrequest_time[ipbxid] = time.time()

                        try:
                            # manage_connection.update_amisocks(ipbxid, self)
                            self._config.update()
                            safe.regular_update()
                        except Exception:
                            logger.exception('%s : failed while updating lists and sockets (select timeout)', ipbxid)
        except Exception:
            logger.exception('select step')
