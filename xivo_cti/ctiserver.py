# -*- coding: utf-8 -*-

# Copyright (C) 2013-2016 Avencall
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
import sys
import time
import threading

from xivo import daemonize
from xivo_cti import config
from xivo_cti import cti_config
from xivo_cti import dao
from xivo_cti import http_app

from xivo_cti.ami import ami_callback_handler
from xivo_cti import channel_updater
from xivo_cti.client_connection import ClientConnection
from xivo_cti.cti.commands.agent_login import AgentLogin
from xivo_cti.cti.commands.agent_logout import AgentLogout
from xivo_cti.cti.commands.answer import Answer
from xivo_cti.cti.commands.call_form_result import CallFormResult
from xivo_cti.cti.commands.chat import Chat
from xivo_cti.cti.commands.dial import Dial
from xivo_cti.cti.commands.directory import Directory
from xivo_cti.cti.commands.attended_transfer import AttendedTransfer
from xivo_cti.cti.commands.direct_transfer import DirectTransfer
from xivo_cti.cti.commands.cancel_transfer import CancelTransfer
from xivo_cti.cti.commands.complete_transfer import CompleteTransfer
from xivo_cti.cti.commands.get_relations import GetRelations
from xivo_cti.cti.commands.hangup import Hangup
from xivo_cti.cti.commands.history import History
from xivo_cti.cti.commands.listen import Listen
from xivo_cti.cti.commands.logout import Logout
from xivo_cti.cti.commands.get_switchboard_directory_headers import GetSwitchboardDirectoryHeaders
from xivo_cti.cti.commands.switchboard_directory_search import SwitchboardDirectorySearch
from xivo_cti.cti.commands.meetme_mute import MeetmeMute
from xivo_cti.cti.commands.meetme_mute import MeetmeUnmute
from xivo_cti.cti.commands.people import PeopleCreatePersonalContact
from xivo_cti.cti.commands.people import PeopleDeletePersonalContact
from xivo_cti.cti.commands.people import PeopleEditPersonalContact
from xivo_cti.cti.commands.people import PeopleExportPersonalContactsCSV
from xivo_cti.cti.commands.people import PeopleImportPersonalContactsCSV
from xivo_cti.cti.commands.people import PeopleFavorites
from xivo_cti.cti.commands.people import PeopleHeaders
from xivo_cti.cti.commands.people import PeoplePersonalContactRaw
from xivo_cti.cti.commands.people import PeoplePersonalContacts
from xivo_cti.cti.commands.people import PeoplePurgePersonalContacts
from xivo_cti.cti.commands.people import PeopleSearch
from xivo_cti.cti.commands.people import PeopleSetFavorite
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
from xivo_cti.cti.commands.vm_txfer import BlindTransferVoicemail, AttendedTransferVoicemail
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

    _BUFSIZE_AMI = 262144
    # BUFSIZE_CTI should be large enough to prevent the SSL layer (when using
    # SSL-wrapped socket) from buffering the application data, i.e. to
    # prevent a CTI connection from being in a state where:
    #  - select(2) doesn't report the socket as being "read-ready"
    #  - there is still data to be read from sock.recv()
    _BUFSIZE_CTI = 65536
    _BUFSIZE_OTHER = 8192

    def __init__(self, bus_publisher):
        self.start_time = time.time()
        self.myipbxid = 'xivo'
        self.interface_ami = None
        self.update_config_list = []
        self.fdlist_full = []
        self.fdlist_interface_cti = {}
        self.fdlist_interface_info = {}
        self.fdlist_interface_webi = {}
        self.fdlist_listen_cti = {}
        self.time_start = time.localtime()
        self._bus_listener_thread = None

    def _set_signal_handlers(self):
        signal.signal(signal.SIGINT, self._sighandler)
        signal.signal(signal.SIGTERM, self._sighandler)

    def _sighandler(self, signum, frame):
        logger.warning('(sighandler) signal %s lineno %s received : quits',
                       signum, frame.f_lineno)
        sys.exit(0)

    def _on_exit(self):
        time_uptime = int(time.time() - time.mktime(self.time_start))
        logger.info('STOPPING %s (pid %d) / uptime %d s (since %s)',
                    self.servername, os.getpid(),
                    time_uptime, time.asctime(self.time_start))

        logger.debug('Stopping the bus listener')
        if self._bus_listener_thread:
            context.get('bus_listener').should_stop = True
            self._bus_listener_thread.join()

        logger.debug('Closing all sockets')
        self._socket_close_all()

        logger.debug('Stopping all remaining threads')
        for t in filter(lambda x: x.getName() not in
                        ['MainThread', 'HTTPServerThread', 'ServiceDiscoveryThread'], threading.enumerate()):
            t._Thread__stop()

        daemonize.unlock_pidfile(config['pidfile'])

    def _setup_token_renewer(self):
        agentd_client = context.get('agentd_client')
        self._token_renewer.subscribe_to_token_change(agentd_client.set_token)
        self._token_renewer.subscribe_to_token_change(cti_config.on_token_change)

    def _daemonize(self):
        if not config['foreground']:
            daemonize.daemonize()
        daemonize.lock_pidfile_or_die(config['pidfile'])

    def setup(self):
        cti_config.update_db_config()
        self._daemonize()
        QueueLogger.init()
        self._set_signal_handlers()

        self._token_renewer = context.get('token_renewer')
        self._setup_token_renewer()

        self.interface_ami = context.get('interface_ami')

        self._cti_msg_codec = context.get('cti_msg_codec')
        self._user_service_manager = context.get('user_service_manager')
        self._funckey_manager = context.get('funckey_manager')
        self._agent_service_manager = context.get('agent_service_manager')
        self._call_form_result_handler = context.get('call_form_result_handler')

        self._bridge_updater = context.get('bridge_updater')

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
        self._agentd_client = context.get('agentd_client')

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

        cache_updater = context.get('cache_updater')
        cache_updater.subscribe_to_bus(context.get('bus_listener'))

    def _register_cti_callbacks(self):
        people_adapter = context.get('people_cti_adapter')
        GetRelations.register_callback_params(people_adapter.get_relations, ['user_id'])
        PeopleSearch.register_callback_params(people_adapter.search, ('auth_token', 'user_id', 'pattern'))
        PeopleFavorites.register_callback_params(people_adapter.favorites, ('auth_token', 'user_id'))
        PeopleSetFavorite.register_callback_params(
            people_adapter.set_favorite,
            ('auth_token', 'user_id', 'source', 'source_entry_id', 'enabled'))
        PeopleHeaders.register_callback_params(people_adapter.get_headers, ('auth_token', 'user_id'))
        PeoplePersonalContacts.register_callback_params(people_adapter.personal_contacts,
                                                        ('auth_token', 'user_id'))
        PeoplePurgePersonalContacts.register_callback_params(people_adapter.purge_personal_contacts,
                                                             ('auth_token', 'user_id'))
        PeoplePersonalContactRaw.register_callback_params(people_adapter.personal_contact_raw,
                                                          ('auth_token', 'user_id', 'source',
                                                           'source_entry_id'))
        PeopleCreatePersonalContact.register_callback_params(people_adapter.create_personal_contact,
                                                             ('auth_token', 'user_id', 'contact_infos'))
        PeopleDeletePersonalContact.register_callback_params(people_adapter.delete_personal_contact,
                                                             ('auth_token', 'user_id', 'source',
                                                              'source_entry_id'))
        PeopleEditPersonalContact.register_callback_params(people_adapter.edit_personal_contact,
                                                           ('auth_token', 'user_id', 'source',
                                                            'source_entry_id', 'contact_infos'))
        PeopleExportPersonalContactsCSV.register_callback_params(people_adapter.export_personal_contacts_csv,
                                                                 ('auth_token', 'user_id'))
        PeopleImportPersonalContactsCSV.register_callback_params(people_adapter.import_personal_contacts_csv,
                                                                 ('auth_token', 'user_id', 'csv_contacts'))

        old_protocol_adapter = context.get('old_protocol_cti_adapter')
        GetSwitchboardDirectoryHeaders.register_callback_params(old_protocol_adapter.get_headers,
                                                                ('auth_token', 'user_id'))
        SwitchboardDirectorySearch.register_callback_params(old_protocol_adapter.lookup,
                                                            ('auth_token', 'user_id', 'pattern'))
        Directory.register_callback_params(old_protocol_adapter.directory_search,
                                           ('auth_token', 'user_id', 'pattern', 'commandid'))

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
        call_manager = context.get('call_manager')
        Dial.register_callback_params(call_manager.call_destination,
                                      ['cti_connection', 'auth_token', 'user_id', 'destination'])
        Hangup.register_callback_params(call_manager.hangup, ['auth_token', 'user_uuid'])
        EnableDND.register_callback_params(self._user_service_manager.enable_dnd, ['user_uuid', 'auth_token'])
        DisableDND.register_callback_params(self._user_service_manager.disable_dnd, ['user_uuid', 'auth_token'])
        EnableRecording.register_callback_params(self._user_service_manager.enable_recording, ['target'])
        DisableRecording.register_callback_params(self._user_service_manager.disable_recording, ['target'])
        EnableFilter.register_callback_params(self._user_service_manager.enable_filter, ['user_uuid', 'auth_token'])
        DisableFilter.register_callback_params(self._user_service_manager.disable_filter, ['user_uuid', 'auth_token'])
        fwd_params = ['user_uuid', 'auth_token', 'destination']
        EnableUnconditionalForward.register_callback_params(self._user_service_manager.enable_unconditional_fwd, fwd_params)
        DisableUnconditionalForward.register_callback_params(self._user_service_manager.disable_unconditional_fwd, fwd_params)
        EnableNoAnswerForward.register_callback_params(self._user_service_manager.enable_rna_fwd, fwd_params)
        DisableNoAnswerForward.register_callback_params(self._user_service_manager.disable_rna_fwd, fwd_params)
        EnableBusyForward.register_callback_params(self._user_service_manager.enable_busy_fwd, fwd_params)
        DisableBusyForward.register_callback_params(self._user_service_manager.disable_busy_fwd, fwd_params)

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

        Logout.register_callback_params(self._user_service_manager.disconnect, ['user_id', 'user_uuid'])

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
        current_call_manager = context.get('current_call_manager')
        AttendedTransfer.register_callback_params(
            current_call_manager.attended_transfer, ['auth_token', 'user_id', 'user_uuid', 'number']
        )
        DirectTransfer.register_callback_params(
            current_call_manager.direct_transfer, ['auth_token', 'user_id', 'user_uuid', 'number']
        )
        BlindTransferVoicemail.register_callback_params(
            current_call_manager.blind_txfer_to_voicemail, ['auth_token', 'user_uuid', 'voicemail_number']
        )
        AttendedTransferVoicemail.register_callback_params(
            current_call_manager.atxfer_to_voicemail, ['auth_token', 'user_uuid', 'voicemail_number']
        )
        CancelTransfer.register_callback_params(
            current_call_manager.cancel_transfer, ['auth_token', 'user_uuid']
        )
        CompleteTransfer.register_callback_params(
            current_call_manager.complete_transfer, ['auth_token', 'user_uuid']
        )
        HoldSwitchboard.register_callback_params(
            current_call_manager.switchboard_hold, ['user_id', 'queue_name']
        )
        ResumeSwitchboard.register_callback_params(
            current_call_manager.switchboard_retrieve_waiting_call,
            ['user_id', 'unique_id', 'cti_connection'],
        )
        Answer.register_callback_params(
            current_call_manager.switchboard_retrieve_waiting_call,
            ['user_id', 'unique_id', 'cti_connection'],
        )
        History.register_callback_params(
            call_history_cti_interface.get_history,
            ['user_id', 'size']
        )
        MeetmeMute.register_callback_params(
            context.get('ami_class').meetmemute, ['meetme_number', 'user_position']
        )
        MeetmeUnmute.register_callback_params(
            context.get('ami_class').meetmeunmute, ['meetme_number', 'user_position']
        )
        Chat.register_callback_params(
            context.get('chat_publisher').on_cti_chat_message,
            ['user_uuid', 'remote_xivo_uuid', 'remote_user_uuid', 'alias', 'text']
        )

    def _register_ami_callbacks(self):
        callback_handler = ami_callback_handler.AMICallbackHandler.get_instance()
        agent_status_parser = context.get('agent_status_parser')

        self._bridge_updater.register_ami_events(callback_handler)
        self._queue_member_updater.register_ami_events(callback_handler)

        callback_handler.register_callback('QueueMemberPause', agent_status_parser.parse_ami_paused)
        callback_handler.register_callback('AgentConnect', agent_status_parser.parse_ami_acd_call_start)
        callback_handler.register_callback('AgentComplete', agent_status_parser.parse_ami_acd_call_end)
        callback_handler.register_userevent_callback('AgentLogin', agent_status_parser.parse_ami_login)
        callback_handler.register_userevent_callback('AgentLogoff', agent_status_parser.parse_ami_logout)

        current_call_parser = context.get('current_call_parser')
        current_call_parser.register_ami_events()

        callback_handler.register_callback('NewCallerId',
                                           channel_updater.parse_new_caller_id)
        callback_handler.register_callback('UserEvent', channel_updater.parse_userevent)

        call_receiver = context.get('call_receiver')
        callback_handler.register_callback('Newstate', call_receiver.handle_newstate)
        callback_handler.register_callback('Hangup', call_receiver.handle_hangup)
        callback_handler.register_callback('DialBegin', call_receiver.handle_dial_begin)
        callback_handler.register_callback('NewChannel', call_receiver.handle_new_channel)

        parser = context.get('switchboard_statistic_ami_parser')
        callback_handler.register_callback('QueueCallerAbandon', parser.on_queue_caller_abandon)
        callback_handler.register_callback('QueueCallerJoin', parser.on_queue_caller_join)
        callback_handler.register_callback('QueueCallerLeave', parser.on_queue_caller_leave)
        callback_handler.register_callback('CEL', parser.on_cel)
        callback_handler.register_callback('BridgeEnter', parser.on_bridge_enter)
        callback_handler.register_callback('VarSet', parser.on_set_var)

        context.get('switchboard_statistic_bus_parser').register_callbacks()

    def _init_statistics_producers(self):
        self._statistics_producer_initializer.init_queue_statistics_producer(self._queue_statistics_producer)

    def _init_agent_availability(self):
        for agent_status in self._agentd_client.agents.get_agent_statuses():
            if agent_status.logged:
                agent_status_cti = AgentStatus.available
            else:
                agent_status_cti = AgentStatus.logged_out
            dao.agent.set_agent_availability(agent_status.id, agent_status_cti)
        context.get('agent_status_adapter').subscribe_all_logged_agents()

    def run(self):
        try:
            with self._token_renewer:
                self.main_loop()
        except Exception:
            logger.exception('main loop has crashed')
        finally:
            self._on_exit()

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

    def main_loop(self):
        self.time_start = time.localtime()
        logger.info('STARTING %s (pid %d))', self.servername, os.getpid())

        logger.info('Retrieving data')
        self.safe = context.get('innerdata')
        self.safe.user_service_manager = self._user_service_manager
        self.safe.queue_member_cti_adapter = self._queue_member_cti_adapter

        dao.instanciate_dao(self.safe, self._queue_member_manager)

        self.safe.init_xod_config()
        self.safe.init_xod_status()
        self.safe.register_cti_handlers()
        self.safe.register_ami_handlers()

        bus_listener = context.get('bus_listener')
        self._bus_listener_thread = threading.Thread(target=bus_listener.run)
        self._bus_listener_thread.start()

        self._queue_member_updater.on_initialization()
        self._queue_member_cti_subscriber.send_cti_event = self.send_cti_event
        self._queue_member_cti_subscriber.subscribe_to_queue_member(self._queue_member_notifier)
        self._queue_member_indexer.subscribe_to_queue_member(self._queue_member_notifier)
        self._queue_statistics_manager.subscribe_to_queue_member(self._queue_member_notifier)
        self._queue_statistics_producer.subscribe_to_queue_member(self._queue_member_notifier)
        self._init_statistics_producers()
        self._init_agent_availability()
        self._queue_member_indexer.initialize(self._queue_member_manager)

        logger.info('Listening for HTTP requests')
        http_interface = http_app.HTTPInterface(config['rest_api'],
                                                context.get('main_thread_proxy'))
        http_interface.start()

        logger.info('Local AMI socket connection')
        self.interface_ami.init_connection()

        self.ami_sock = self.interface_ami.connect()
        if not self.ami_sock:
            self._on_ami_down()

        logger.info('Listening sockets')
        socktimeout = float(config['socket_timeout'])
        socket.setdefaulttimeout(socktimeout)

        incoming_tcp = {'CTI': (config['client']['listen'],
                                config['client']['port'],
                                config['client']['enabled']),
                        'INFO': (config['info']['listen'],
                                 config['info']['port'],
                                 config['info']['enabled']),
                        'WEBI': (config['update_events_socket']['listen'],
                                 config['update_events_socket']['port'],
                                 config['update_events_socket']['enabled'])}
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
        while True:
            self.select_step()

    def _init_tcp_socket(self, kind, bind, port):
        logger.debug('init tcp socket %s %s %s', kind, bind, port)
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

    def send_to_cti_client(self, who, what):
        (ipbxid, userid) = who.split('/')
        for interface_cti in self.fdlist_interface_cti.itervalues():
            if interface_cti.connection_details.get('userid') == userid:
                interface_cti.reply(what)

    def disconnect_iface(self, iface, cause):
        socket = iface.connid
        iface.disconnected(cause)
        if socket:
            socket.close()
            self._remove_from_fdlist(socket)

    def _init_socket(self):
        fdlist_full = []
        try:
            fdtodel = []
            for cn in self.fdlist_interface_cti:
                if cn.isClosed and cn not in fdtodel:
                    fdtodel.append(cn)
            for cn in fdtodel:
                del self.fdlist_interface_cti[cn]

            fdlist_full.append(self._task_queue)
            fdlist_full.append(self.ami_sock)
            fdlist_full.extend(self.fdlist_listen_cti)
            fdlist_full.extend(self.fdlist_interface_cti)
            fdlist_full.extend(self.fdlist_interface_webi)
            fdlist_full.extend(self.fdlist_interface_info)

            writefds = []
            for iconn in self.fdlist_interface_cti:
                if iconn.need_sending():
                    writefds.append(iconn)

            timeout = self._task_scheduler.timeout()
            if timeout is None:
                result = select.select(fdlist_full, writefds, [])
            else:
                result = select.select(fdlist_full, writefds, [], timeout)
            return result

        except Exception:
            logger.exception('(select) fdlist_full=%s', fdlist_full)
            sys.exit(5)

    def _socket_close_all(self):
        cause = DisconnectCause.by_server_stop

        for interface_cti in self.fdlist_interface_cti.itervalues():
            self._broadcast_cti_group.remove(interface_cti)
            interface_cti.disconnected(cause)

        for interface_info in self.fdlist_interface_info.itervalues():
            interface_info.disconnected(cause)

        for interface_webi in self.fdlist_interface_webi.itervalues():
            interface_webi.disconnected(cause)

    def _socket_ami_read(self, sel_i):
        buf = sel_i.recv(self._BUFSIZE_AMI)
        if not buf:
            self._on_ami_down()
        else:
            self.interface_ami.handle_event(buf)

    def _socket_detect_new_tcp_connection(self, sel_i):
        [kind, nmax] = self.fdlist_listen_cti[sel_i].split(':')
        [socketobject, address] = sel_i.accept()
        if socketobject:
            if kind == 'CTI':
                socketobject = ClientConnection(socketobject, address)
                interface = interface_cti.CTI(self,
                                              self._broadcast_cti_group,
                                              self._cti_msg_codec.new_decoder(),
                                              self._cti_msg_codec.new_encoder())
                self.fdlist_interface_cti[socketobject] = interface
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
                    msg = sel_i.recv(self._BUFSIZE_CTI)
                    closemenow = self.manage_tcp_connections(sel_i, msg, interface_obj)
                except ClientConnection.CloseException:
                    self.disconnect_iface(interface_obj, DisconnectCause.broken_pipe)
            else:
                try:
                    msg = sel_i.recv(self._BUFSIZE_OTHER, socket.MSG_DONTWAIT)
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
                self.disconnect_iface(interface_obj, DisconnectCause.by_client)
        except Exception:
            logger.exception('[%s] %s', interface_obj, sel_i)
            logger.warning('unexpected socket breakup')
            self.disconnect_iface(interface_obj, DisconnectCause.broken_pipe)

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
                    self.update_config_list.pop(self.update_config_list.index('xivo[cticonfig,update]'))
            except Exception:
                logger.exception('failed while executing xivo[cticonfig,update]')
            try:
                while self.update_config_list:
                    msg = self.update_config_list.pop()
                    self.safe.update_config_list('%ss' % msg['object_name'], msg['state'], msg['id'])
            except Exception:
                logger.exception('Config reload')

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
