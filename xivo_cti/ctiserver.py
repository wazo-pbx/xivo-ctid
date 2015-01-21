# -*- coding: utf-8 -*-

# Copyright (C) 2013-2015 Avencall
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

import logging
import os
import select
import signal
import socket
import ssl
import sys
import time
import threading

from xivo import daemonize
from xivo.xivo_logging import setup_logging
from xivo_cti import config
from xivo_cti import BUFSIZE_LARGE
from xivo_cti import cti_config
from xivo_cti import SSLPROTO
from xivo_cti import dao
from xivo_cti import message_hook
from xivo_cti.ami import ami_callback_handler
from xivo_cti import channel_updater
from xivo_cti.client_connection import ClientConnection
from xivo_cti.cti.commands.agent_login import AgentLogin
from xivo_cti.cti.commands.agent_logout import AgentLogout
from xivo_cti.cti.commands.answer import Answer
from xivo_cti.cti.commands.call_form_result import CallFormResult
from xivo_cti.cti.commands.dial import Dial
from xivo_cti.cti.commands.attended_transfer import AttendedTransfer
from xivo_cti.cti.commands.direct_transfer import DirectTransfer
from xivo_cti.cti.commands.cancel_transfer import CancelTransfer
from xivo_cti.cti.commands.complete_transfer import CompleteTransfer
from xivo_cti.cti.commands.hangup import Hangup
from xivo_cti.cti.commands.history import History
from xivo_cti.cti.commands.listen import Listen
from xivo_cti.cti.commands.logout import Logout
from xivo_cti.cti.commands.people import PeopleHeaders
from xivo_cti.cti.commands.people import PeopleSearch
from xivo_cti.cti.commands.queue_add import QueueAdd
from xivo_cti.cti.commands.queue_pause import QueuePause
from xivo_cti.cti.commands.queue_remove import QueueRemove
from xivo_cti.cti.commands.queue_unpause import QueueUnPause
from xivo_cti.cti.commands.register_agent_status import RegisterAgentStatus
from xivo_cti.cti.commands.register_endpoint_status import RegisterEndpointStatus
from xivo_cti.cti.commands.register_user_status import RegisterUserStatus
from xivo_cti.cti.commands.unregister_agent_status import UnregisterAgentStatus
from xivo_cti.cti.commands.unregister_user_status import UnregisterUserStatus
from xivo_cti.cti.commands.unregister_endpoint_status import UnregisterEndpointStatus
from xivo_cti.cti.commands.subscribe import SubscribeCurrentCalls, \
    SubscribeMeetmeUpdate, SubscribeQueueEntryUpdate
from xivo_cti.cti.commands.subscribetoqueuesstats import SubscribeToQueuesStats
from xivo_cti.cti.commands.hold_switchboard import HoldSwitchboard
from xivo_cti.cti.commands.resume_switchboard import ResumeSwitchboard
from xivo_cti.cti.commands.set_forward import DisableBusyForward, \
    DisableNoAnswerForward, DisableUnconditionalForward, EnableBusyForward, \
    EnableNoAnswerForward, EnableUnconditionalForward
from xivo_cti.cti.commands.set_user_service import DisableDND, DisableFilter, EnableDND, EnableFilter, \
    EnableRecording, DisableRecording
from xivo_cti.services.funckey import manager as funckey_manager
from xivo_cti.services.call_history import cti_interface as call_history_cti_interface
from xivo_cti.interfaces import interface_cti
from xivo_cti.interfaces import interface_info
from xivo_cti.interfaces import interface_webi
from xivo_cti.interfaces.interfaces import DisconnectCause
from xivo_cti.queue_logger import QueueLogger
from xivo_cti.services import queue_entry_manager
from xivo_cti.services.agent.status import AgentStatus
from xivo_cti.services.meetme import service_manager as meetme_service_manager_module
from xivo_cti.statistics import queue_statistics_manager
from xivo_cti.statistics import queue_statistics_producer
from xivo_cti.ioc.context import context

logger = logging.getLogger('main')


class CTIServer(object):

    servername = 'XiVO CTI Server'

    def __init__(self):
        self.start_time = time.time()
        self.myipbxid = 'xivo'
        self.interface_ami = None
        self.update_config_list = []

    def _set_signal_handlers(self):
        signal.signal(signal.SIGINT, self._sighandler)
        signal.signal(signal.SIGTERM, self._sighandler)

    def _sighandler(self, signum, frame):
        logger.warning('(sighandler) signal %s lineno %s (atq = %s) received : quits',
                       signum, frame.f_lineno, self.askedtoquit)
        for t in filter(lambda x: x.getName() != 'MainThread', threading.enumerate()):
            t._Thread__stop()
        self.askedtoquit = True

    def _set_logger(self):
        setup_logging(config['logfile'], config['foreground'], config['debug'])

    def _daemonize(self):
        if not config['foreground']:
            daemonize.daemonize()
        daemonize.lock_pidfile_or_die(config['pidfile'])

    def setup(self):
        cti_config.update_db_config()
        self._set_logger()
        self._daemonize()
        QueueLogger.init()
        self._set_signal_handlers()

        context.get('status_forwarder').run()

        self.interface_ami = context.get('interface_ami')

        self._cti_msg_codec = context.get('cti_msg_codec')
        self._user_service_manager = context.get('user_service_manager')
        self._funckey_manager = context.get('funckey_manager')
        self._agent_service_manager = context.get('agent_service_manager')
        self._call_form_result_handler = context.get('call_form_result_handler')

        self._presence_service_executor = context.get('presence_service_executor')
        self._statistics_notifier = context.get('statistics_notifier')
        self._queue_statistics_producer = context.get('queue_statistics_producer')

        self._queue_member_notifier = context.get('queue_member_notifier')
        self._queue_member_updater = context.get('queue_member_updater')
        self._queue_member_manager = context.get('queue_member_manager')
        self._queue_member_cti_adapter = context.get('queue_member_cti_adapter')
        self._queue_member_cti_subscriber = context.get('queue_member_cti_subscriber')
        self._queue_member_indexer = context.get('queue_member_indexer')

        self._user_service_manager.presence_service_executor = self._presence_service_executor

        self._queue_entry_manager = context.get('queue_entry_manager')
        self._queue_statistics_manager = context.get('queue_statistics_manager')
        self._queue_entry_notifier = context.get('queue_entry_notifier')

        self._task_queue = context.get('task_queue')
        self._task_scheduler = context.get('task_scheduler')

        self._agent_availability_updater = context.get('agent_availability_updater')
        self._agent_service_cti_parser = context.get('agent_service_cti_parser')

        self._statistics_producer_initializer = context.get('statistics_producer_initializer')

        self._agent_status_manager = context.get('agent_status_manager')

        self._agent_client = context.get('agent_client')
        self._agent_client.connect()

        self._broadcast_cti_group = context.get('broadcast_cti_group')

        self._flusher = context.get('flusher')

        context.get('user_service_notifier').send_cti_event = self.send_cti_event
        context.get('user_service_notifier').ipbx_id = self.myipbxid

        queue_entry_manager.register_events()
        queue_statistics_manager.register_events()
        queue_statistics_producer.register_events()
        meetme_service_manager_module.register_callbacks()

        meetme_service_manager = context.get('meetme_service_manager')
        meetme_service_manager.initialize()

        self._register_cti_callbacks()
        self._register_ami_callbacks()
        self._register_message_hooks()

    def _register_cti_callbacks(self):
        people_adapter = context.get('people_cti_adapter')
        PeopleSearch.register_callback_params(people_adapter.search, ('user_id', 'pattern'))
        PeopleHeaders.register_callback_params(people_adapter.get_headers, ['user_id'])
        status_forwarder = context.get('status_forwarder')
        RegisterAgentStatus.register_callback_params(
            status_forwarder.agent_status_notifier.register,
            ['cti_connection', 'agent_ids'],
        )
        RegisterEndpointStatus.register_callback_params(
            status_forwarder.endpoint_status_notifier.register,
            ['cti_connection', 'endpoint_ids'],
        )
        RegisterUserStatus.register_callback_params(
            status_forwarder.user_status_notifier.register,
            ['cti_connection', 'user_ids'],
        )
        UnregisterAgentStatus.register_callback_params(
            status_forwarder.agent_status_notifier.unregister,
            ['cti_connection', 'agent_ids'],
        )
        UnregisterUserStatus.register_callback_params(
            status_forwarder.user_status_notifier.unregister,
            ['cti_connection', 'user_ids'],
        )
        UnregisterEndpointStatus.register_callback_params(
            status_forwarder.endpoint_status_notifier.unregister,
            ['cti_connection', 'endpoint_ids'],
        )
        CallFormResult.register_callback_params(
            self._call_form_result_handler.parse, ['user_id', 'variables'],
        )
        Dial.register_callback_params(self._user_service_manager.call_destination,
                                      ['cti_connection', 'user_id', 'destination'])
        EnableDND.register_callback_params(self._user_service_manager.enable_dnd, ['user_id'])
        DisableDND.register_callback_params(self._user_service_manager.disable_dnd, ['user_id'])
        EnableRecording.register_callback_params(self._user_service_manager.enable_recording, ['target'])
        DisableRecording.register_callback_params(self._user_service_manager.disable_recording, ['target'])
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
        SubscribeToQueuesStats.register_callback_params(self._queue_statistics_manager.get_all_queue_summary)
        SubscribeToQueuesStats.register_callback_params(self._queue_entry_manager.publish_all_realtime_stats, ['cti_connection'])
        SubscribeQueueEntryUpdate.register_callback_params(
            self._queue_entry_notifier.subscribe, ['cti_connection', 'queue_id'])

        AgentLogin.register_callback_params(
            self._agent_service_manager.on_cti_agent_login,
            ['user_id', 'agent_id', 'agent_phone_number']
        )
        AgentLogout.register_callback_params(
            self._agent_service_manager.on_cti_agent_logout,
            ['user_id', 'agent_id']
        )
        Listen.register_callback_params(
            self._agent_service_manager.on_cti_listen,
            ['user_id', 'destination']
        )

        Logout.register_callback_params(self._user_service_manager.disconnect, ['user_id'])

        QueueAdd.register_callback_params(
            self._agent_service_cti_parser.queue_add,
            ['member', 'queue']
        )
        QueueRemove.register_callback_params(
            self._agent_service_cti_parser.queue_remove,
            ['member', 'queue']
        )
        QueuePause.register_callback_params(
            self._agent_service_cti_parser.queue_pause,
            ['member', 'queue']
        )
        QueueUnPause.register_callback_params(
            self._agent_service_cti_parser.queue_unpause,
            ['member', 'queue']
        )

        SubscribeMeetmeUpdate.register_callback_params(
            context.get('meetme_service_notifier').subscribe,
            ['cti_connection']
        )
        SubscribeCurrentCalls.register_callback_params(
            context.get('current_call_notifier').subscribe,
            ['cti_connection']
        )
        Hangup.register_callback_params(
            context.get('current_call_manager').hangup,
            ['user_id']
        )
        AttendedTransfer.register_callback_params(
            context.get('current_call_manager').attended_transfer,
            ['user_id', 'number']
        )
        DirectTransfer.register_callback_params(
            context.get('current_call_manager').direct_transfer,
            ['user_id', 'number']
        )
        CancelTransfer.register_callback_params(
            context.get('current_call_manager').cancel_transfer,
            ['user_id']
        )
        CompleteTransfer.register_callback_params(
            context.get('current_call_manager').complete_transfer,
            ['user_id']
        )
        HoldSwitchboard.register_callback_params(
            context.get('current_call_manager').switchboard_hold,
            ['user_id', 'queue_name']
        )
        ResumeSwitchboard.register_callback_params(
            context.get('current_call_manager').switchboard_retrieve_waiting_call,
            ['user_id', 'unique_id', 'cti_connection'],
        )
        Answer.register_callback_params(
            context.get('current_call_manager').switchboard_retrieve_waiting_call,
            ['user_id', 'unique_id', 'cti_connection'],
        )
        History.register_callback_params(
            call_history_cti_interface.get_history,
            ['user_id', 'mode', 'size']
        )

    def _register_ami_callbacks(self):
        callback_handler = ami_callback_handler.AMICallbackHandler.get_instance()
        agent_status_parser = context.get('agent_status_parser')

        self._queue_member_updater.register_ami_events(callback_handler)

        callback_handler.register_callback('QueueMemberPaused', agent_status_parser.parse_ami_paused)
        callback_handler.register_callback('AgentConnect', agent_status_parser.parse_ami_acd_call_start)
        callback_handler.register_callback('AgentComplete', agent_status_parser.parse_ami_acd_call_end)
        callback_handler.register_userevent_callback('AgentLogin', agent_status_parser.parse_ami_login)
        callback_handler.register_userevent_callback('AgentLogoff', agent_status_parser.parse_ami_logout)

        current_call_parser = context.get('current_call_parser')
        current_call_parser.register_ami_events()

        callback_handler.register_callback('NewCallerId',
                                           channel_updater.parse_new_caller_id)
        callback_handler.register_callback('UserEvent', channel_updater.parse_userevent)
        callback_handler.register_callback('Hold', channel_updater.parse_hold)

        call_receiver = context.get('call_receiver')
        callback_handler.register_callback('Newstate', call_receiver.handle_newstate)
        callback_handler.register_callback('Hangup', call_receiver.handle_hangup)
        callback_handler.register_callback('Dial', call_receiver.handle_dial)
        callback_handler.register_callback('Bridge', call_receiver.handle_bridge)
        callback_handler.register_callback('NewChannel', call_receiver.handle_new_channel)
        callback_handler.register_callback('Masquerade', call_receiver.handle_masquerade)

    def _register_message_hooks(self):
        message_hook.add_hook([('function', 'updateconfig'),
                               ('listname', 'users')],
                              lambda x: funckey_manager.parse_update_user_config(self._funckey_manager, x))

    def _init_statistics_producers(self):
        self._statistics_producer_initializer.init_queue_statistics_producer(self._queue_statistics_producer)

    def _init_agent_availability(self):
        for agent_status in self._agent_client.get_agent_statuses():
            if agent_status.logged:
                agent_status_cti = AgentStatus.available
            else:
                agent_status_cti = AgentStatus.logged_out
            dao.agent.set_agent_availability(agent_status.id, agent_status_cti)
        context.get('agent_status_adapter').subscribe_all_logged_agents()

    def run(self):
        while True:
            try:
                self.main_loop()
            except Exception:
                logger.exception('main loop has crashed ... retrying in 5 seconds ...')
                time.sleep(5)

    def manage_tcp_connections(self, sel_i, msg, kind):
        """
        Dispatches the message's handling according to the connection's kind.
        """
        closemenow = False
        if not isinstance(kind, str):  # CTI, INFO, WEBI
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

    def _on_cti_login_auth_timeout(self, connc):
        connc.close()
        if connc in self.fdlist_interface_cti:
            del self.fdlist_interface_cti[connc]

    def main_loop(self):
        self.askedtoquit = False
        self.time_start = time.localtime()
        logger.info('STARTING %s (pid %d))', self.servername, os.getpid())

        self._task_queue.clear()
        self._task_scheduler.clear()

        logger.info('Connecting to bus')
        bus_producer = context.get('bus_producer')
        if not bus_producer.connected:
            bus_producer.connect()
        bus_producer.declare_exchange(name=config['bus']['exchange_name'],
                                      exchange_type=config['bus']['exchange_type'],
                                      durable=config['bus']['exchange_durable'])

        logger.info('Retrieving data')
        self.safe = context.get('innerdata')
        self.safe.user_service_manager = self._user_service_manager
        self.safe.queue_member_cti_adapter = self._queue_member_cti_adapter

        dao.instanciate_dao(self.safe, self._queue_member_manager)

        self.safe.init_xod_config()
        self.safe.init_xod_status()
        self.safe.register_cti_handlers()
        self.safe.register_ami_handlers()
        self.safe.update_directories()

        self._queue_member_updater.on_initialization()
        self._queue_member_cti_subscriber.send_cti_event = self.send_cti_event
        self._queue_member_cti_subscriber.subscribe_to_queue_member(self._queue_member_notifier)
        self._queue_member_indexer.subscribe_to_queue_member(self._queue_member_notifier)
        self._queue_statistics_manager.subscribe_to_queue_member(self._queue_member_notifier)
        self._queue_statistics_producer.subscribe_to_queue_member(self._queue_member_notifier)
        self._init_statistics_producers()
        self._init_agent_availability()
        self._queue_member_indexer.initialize(self._queue_member_manager)

        logger.info('Local AMI socket connection')
        self.interface_ami.init_connection()

        self.ami_sock = self.interface_ami.connect()
        if not self.ami_sock:
            self._on_ami_down()

        logger.info('Listening sockets')
        xivoconf_general = config['main']
        socktimeout = float(xivoconf_general.get('sockettimeout', '2'))
        socket.setdefaulttimeout(socktimeout)

        self.fdlist_interface_cti = {}
        self.fdlist_interface_info = {}
        self.fdlist_interface_webi = {}
        self.fdlist_listen_cti = {}

        incoming_tcp = xivoconf_general.get('incoming_tcp', {})
        for kind, bind_and_port in incoming_tcp.iteritems():
            allow_kind = True
            if len(bind_and_port) > 2:
                allow_kind = bind_and_port[2]
            if not allow_kind:
                logger.warning('%s kind listening socket has been explicitly disabled', kind)
                continue
            bind, port = bind_and_port[:2]
            self._init_tcp_socket(kind, bind, port)

        logger.info('CTI Fully Booted in %.6f seconds', (time.time() - self.start_time))
        while not self.askedtoquit:
            self.select_step()

    def _init_tcp_socket(self, kind, bind, port):
        try:
            trueport = int(port)
            gai = socket.getaddrinfo(bind, trueport, 0, socket.SOCK_STREAM, socket.SOL_TCP)
            if not gai:
                return
            (afinet, socktype, proto, dummy, bindtuple) = gai[0]
            UIsock = socket.socket(afinet, socktype)
            UIsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            UIsock.bind(bindtuple)
            UIsock.listen(10)
            self.fdlist_listen_cti[UIsock] = '%s:%s' % (kind, 1)
        except Exception:
            logger.exception('tcp %s %d', bind, trueport)

    def _on_ami_down(self):
        logger.warning('AMI: CLOSING (%s)', time.asctime())
        logger.info('shutting down xivo-ctid')
        sys.exit(2)

    def get_connected(self, tomatch):
        clist = []
        for interface_cti in self.fdlist_interface_cti.itervalues():
            userid = interface_cti.connection_details.get('userid')
            if self.safe.user_match(userid, tomatch):
                clist.append(interface_cti)
        return clist

    def sendsheettolist(self, tsl, payload):
        for k in tsl:
            k.reply(payload)

    def send_cti_event(self, event):
        self._broadcast_cti_group.send_message(event)
        message_hook.run_hooks(event)

    def set_transfer_socket(self, faxobj, direction):
        for iconn, interface_cti in self.fdlist_interface_cti.iteritems():
            peername = '%s:%d' % iconn.getpeername()
            if peername == faxobj.socketref:
                interface_cti.set_as_transfer(direction, faxobj)
                break

    def send_to_cti_client(self, who, what):
        (ipbxid, userid) = who.split('/')
        for interface_cti in self.fdlist_interface_cti.itervalues():
            if interface_cti.connection_details.get('userid') == userid:
                interface_cti.reply(what)

    def _init_socket(self):
        try:
            fdtodel = []
            for cn in self.fdlist_interface_cti:
                if cn.isClosed and cn not in fdtodel:
                    fdtodel.append(cn)
            for cn in fdtodel:
                del self.fdlist_interface_cti[cn]

            self.fdlist_full = []
            self.fdlist_full.append(self._task_queue)
            self.fdlist_full.append(self.ami_sock)
            self.fdlist_full.extend(self.fdlist_listen_cti)
            self.fdlist_full.extend(self.fdlist_interface_cti)
            self.fdlist_full.extend(self.fdlist_interface_webi)
            self.fdlist_full.extend(self.fdlist_interface_info)

            writefds = []
            for iconn in self.fdlist_interface_cti:
                if iconn.need_sending():
                    writefds.append(iconn)

            timeout = self._task_scheduler.timeout()
            if timeout is None:
                result = select.select(self.fdlist_full, writefds, [])
            else:
                result = select.select(self.fdlist_full, writefds, [], timeout)
            return result

        except Exception:
            logger.exception('(select) probably Ctrl-C or daemon stop or daemon restart ...')
            logger.warning('(select) self.askedtoquit=%s fdlist_full=%s', self.askedtoquit, self.fdlist_full)

            self._socket_close_all()

            if self.askedtoquit:
                time_uptime = int(time.time() - time.mktime(self.time_start))
                logger.info('STOPPING %s (pid %d) / uptime %d s (since %s)',
                            self.servername, os.getpid(),
                            time_uptime, time.asctime(self.time_start))
                for t in filter(lambda x: x.getName() != 'MainThread', threading.enumerate()):
                    print '--- (stop) killing thread <%s>' % t.getName()
                    t._Thread__stop()
                daemonize.unlock_pidfile(config['pidfile'])
                sys.exit(5)
            else:
                self.askedtoquit = True
                for t in filter(lambda x: x.getName() != 'MainThread', threading.enumerate()):
                    print '--- (reload) the thread <%s> remains' % t.getName()
                return (None, None, None)

    def _socket_close_all(self):
        cause = DisconnectCause.by_server_stop if self.askedtoquit else DisconnectCause.by_server_reload
        for s in self.fdlist_full:
            if s in self.fdlist_interface_cti:
                self.fdlist_interface_cti[s].disconnected(cause)
            elif s in self.fdlist_interface_info:
                self.fdlist_interface_info[s].disconnected(cause)
            elif s in self.fdlist_interface_webi:
                self.fdlist_interface_webi[s].disconnected(cause)
            if not isinstance(s, int):
                s.close()

    def _socket_ami_read(self, sel_i):
        buf = sel_i.recv(BUFSIZE_LARGE)
        if not buf:
            self._on_ami_down()
        else:
            self.interface_ami.handle_event(buf)

    def _socket_detect_new_tcp_connection(self, sel_i):
        [kind, nmax] = self.fdlist_listen_cti[sel_i].split(':')
        [socketobject, address] = sel_i.accept()

        if kind == 'CTI':
            socketobject = ClientConnection(socketobject, address)
            interface = interface_cti.CTI(self, self._cti_msg_codec.new_decoder(), self._cti_msg_codec.new_encoder())
        elif kind == 'CTIS':
            certfile = config['main']['certfile']
            keyfile = config['main']['keyfile']
            try:
                connstream = ssl.wrap_socket(socketobject,
                                             server_side=True,
                                             certfile=certfile,
                                             keyfile=keyfile,
                                             ssl_version=SSLPROTO)
                socketobject = ClientConnection(connstream, address)
                interface = interface_cti.CTIS(self, self._cti_msg_codec.new_decoder(), self._cti_msg_codec.new_encoder())
            except ssl.SSLError:
                logger.exception('%s:%s:%d cert=%s key=%s)',
                                 kind, address[0], address[1],
                                 certfile,
                                 keyfile)
                socketobject.close()
                socketobject = None

        if socketobject:
            if kind in ['CTI', 'CTIS']:
                logintimeout = int(config['main'].get('logintimeout', 5))
                interface.login_task = self._task_scheduler.schedule(logintimeout, self._on_cti_login_auth_timeout, socketobject)
                self.fdlist_interface_cti[socketobject] = interface
                self._broadcast_cti_group.add(interface)
            elif kind == 'INFO':
                interface = interface_info.INFO(self)
                self.fdlist_interface_info[socketobject] = interface
            elif kind == 'WEBI':
                interface = interface_webi.WEBI(self, self._queue_member_updater)
                self.fdlist_interface_webi[socketobject] = interface

            interface.connected(socketobject)
        else:
            logger.warning('socketobject is not defined ...')

    def _socket_established_read(self, sel_i, interface_obj):
        try:
            requester = '%s:%d' % sel_i.getpeername()[:2]
            closemenow = False
            if isinstance(sel_i, ClientConnection):
                try:
                    msg = sel_i.recv(BUFSIZE_LARGE)
                    closemenow = self.manage_tcp_connections(sel_i, msg, interface_obj)
                except ClientConnection.CloseException:
                    interface_obj.disconnected(DisconnectCause.broken_pipe)
                    self._remove_from_fdlist(sel_i)
            else:
                try:
                    msg = sel_i.recv(BUFSIZE_LARGE, socket.MSG_DONTWAIT)
                except socket.error:
                    logger.exception('connection to %s (%s)', requester, interface_obj)
                    msg = ''

                if msg:
                    try:
                        closemenow = self.manage_tcp_connections(sel_i, msg, interface_obj)
                    except Exception:
                        logger.exception('handling %s (%s)', requester, interface_obj)
                else:
                    closemenow = True

            if closemenow:
                interface_obj.disconnected(DisconnectCause.by_client)
                sel_i.close()
                self._remove_from_fdlist(sel_i)
        except Exception:
            logger.exception('[%s] %s', interface_obj, sel_i)
            logger.warning('unexpected socket breakup')
            interface_obj.disconnected(DisconnectCause.broken_pipe)
            sel_i.close()
            self._remove_from_fdlist(sel_i)

    def _remove_from_fdlist(self, conn):
        if conn in self.fdlist_interface_cti:
            del self.fdlist_interface_cti[conn]
        elif conn in self.fdlist_interface_info:
            del self.fdlist_interface_info[conn]
        elif conn in self.fdlist_interface_webi:
            del self.fdlist_interface_webi[conn]

    def _update_safe_list(self):
        if self.update_config_list:
            try:
                if 'xivo[cticonfig,update]' in self.update_config_list:
                    cti_config.update_db_config()
                    self.safe.update_directories()
                    self.update_config_list.pop(self.update_config_list.index('xivo[cticonfig,update]'))
            except Exception:
                logger.exception('failed while executing xivo[cticonfig,update]')
            try:
                while self.update_config_list:
                    msg = self.update_config_list.pop()
                    self.safe.update_config_list('%ss' % msg['object_name'], msg['state'], msg['id'])
            except Exception:
                logger.exception('Config reload (computed timeout)')

    def select_step(self):
        sels_i, sels_o, sels_e = self._init_socket()

        try:
            for sel_o in sels_o:
                try:
                    sel_o.process_sending()
                except ClientConnection.CloseException:
                    if sel_o in self.fdlist_interface_cti:
                        kind = self.fdlist_interface_cti[sel_o]
                        kind.disconnected(DisconnectCause.broken_pipe)
                        sel_o.close()
                        del self.fdlist_interface_cti[sel_o]
        except Exception:
            logger.exception('Socket writer')

        try:
            for sel_i in sels_i:
                # these AMI connection are used in order to manage AMI commands and events
                if sel_i == self.ami_sock:
                    self._socket_ami_read(sel_i)
                # task queue
                elif sel_i == self._task_queue:
                    self._task_queue.run()
                # the new TCP connections (CTI, WEBI, INFO) are catched here
                elif sel_i in self.fdlist_listen_cti:
                    self._socket_detect_new_tcp_connection(sel_i)
                # CTI
                elif sel_i in self.fdlist_interface_cti:
                    interface_obj = self.fdlist_interface_cti[sel_i]
                    self._socket_established_read(sel_i, interface_obj)
                # INFO
                elif sel_i in self.fdlist_interface_info:
                    interface_obj = self.fdlist_interface_info[sel_i]
                    self._socket_established_read(sel_i, interface_obj)
                # WEBI
                elif sel_i in self.fdlist_interface_webi:
                    interface_obj = self.fdlist_interface_webi[sel_i]
                    self._socket_established_read(sel_i, interface_obj)
        except Exception:
            logger.exception('Socket Reader')

        try:
            self._task_scheduler.run()
            self._update_safe_list()
        except Exception:
            logger.exception('error')

        self._flusher.flush()
