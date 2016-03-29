# -*- coding: utf-8 -*-

# Copyright (C) 2009-2016 Avencall
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

from functools import partial

from xivo import caller_id
from xivo_cti import dao
from xivo_cti.ami.ami_response_handler import AMIResponseHandler
from xivo_cti.bus_listener import bus_listener_thread, ack_bus_message
from xivo_cti.cti.cti_message_formatter import CTIMessageFormatter
from xivo_cti.database import user_db
from xivo_cti.exception import NoSuchUserException
from xivo_cti.model.destination_factory import DestinationFactory
from xivo_cti.tools.extension import InvalidExtension

logger = logging.getLogger(__name__)

RESPONSE = 'Response'
SUCCESS = 'Success'
MESSAGE = 'Message'


class UserServiceManager(object):

    def __init__(self,
                 user_service_notifier,
                 agent_service_manager,
                 presence_service_manager,
                 funckey_manager,
                 device_manager,
                 ami_class,
                 ami_callback_handler,
                 call_manager,
                 confd_client,
                 async_runner,
                 bus_listener,
                 task_queue):
        self.user_service_notifier = user_service_notifier
        self.agent_service_manager = agent_service_manager
        self.presence_service_manager = presence_service_manager
        self.funckey_manager = funckey_manager
        self.device_manager = device_manager
        self.dao = dao
        self.ami_class = ami_class
        self._ami_callback_handler = ami_callback_handler
        self._call_manager = call_manager
        self._client = confd_client
        self._runner = async_runner
        self._task_queue = task_queue
        services_routing_key = 'config.users.*.services.*.updated'
        bus_listener.add_callback(services_routing_key, self._on_bus_services_message_event)

        forwards_routing_key = 'config.users.*.forwards.*.updated'
        bus_listener.add_callback(forwards_routing_key, self._on_bus_forwards_message_event)

    def call_destination(self, client_connection, user_id, url_or_exten):
        if DestinationFactory.is_destination_url(url_or_exten):
            exten = DestinationFactory.make_from(url_or_exten).to_exten()
        elif caller_id.is_complete_caller_id(url_or_exten):
            exten = caller_id.extract_number(url_or_exten)
        else:
            exten = url_or_exten

        try:
            action_id = self._dial(user_id, exten)
            self._register_originate_response_callback(action_id, client_connection, user_id, exten)
        except InvalidExtension as e:
            self._on_originate_error(client_connection,
                                     user_id,
                                     exten,
                                     "Invalid extension '{exten}'".format(exten=e.exten))

    def connect(self, user_id, state):
        self.dao.user.connect(user_id)
        self.set_presence(user_id, state)

    def enable_dnd(self, user_id):
        logger.debug('Enable DND called for user_id %s', user_id)
        self._async_set_service(user_id, 'dnd', True)

    def disable_dnd(self, user_id):
        logger.debug('Disable DND called for user_id %s', user_id)
        self._async_set_service(user_id, 'dnd', False)

    def set_dnd(self, user_id, status):
        self.enable_dnd(user_id) if status else self.disable_dnd(user_id)

    def enable_filter(self, user_id):
        logger.debug('Enable IncallFilter called for user_id %s', user_id)
        self._async_set_service(user_id, 'incallfilter', True)

    def disable_filter(self, user_id):
        logger.debug('Disable IncallFilter called for user_id %s', user_id)
        self._async_set_service(user_id, 'incallfilter', False)

    def enable_unconditional_fwd(self, user_id, destination):
        if not destination:
            self.disable_unconditional_fwd(user_id, destination)
            return
        logger.debug('Enable Unconditional called for user_id %s', user_id)
        self._async_set_forward(user_id, 'unconditional', True, destination)

    def disable_unconditional_fwd(self, user_id, destination):
        logger.debug('Disable Unconditional called for user_id %s', user_id)
        self._async_set_forward(user_id, 'unconditional', False, destination)

    def enable_rna_fwd(self, user_id, destination):
        if not destination:
            self.disable_rna_fwd(user_id, destination)
            return
        logger.debug('Enable NoAnswer called for user_id %s', user_id)
        self._async_set_forward(user_id, 'noanswer', True, destination)

    def disable_rna_fwd(self, user_id, destination):
        logger.debug('Disable NoAnswer called for user_id %s', user_id)
        self._async_set_forward(user_id, 'noanswer', False, destination)

    def enable_busy_fwd(self, user_id, destination):
        if not destination:
            self.disable_busy_fwd(user_id, destination)
            return
        logger.debug('Enable Busy called for user_id %s', user_id)
        self._async_set_forward(user_id, 'busy', True, destination)

    def disable_busy_fwd(self, user_id, destination):
        logger.debug('Disable Busy called for user_id %s', user_id)
        self._async_set_forward(user_id, 'busy', False, destination)

    def disconnect(self, user_id):
        self.dao.user.disconnect(user_id)
        self.set_presence(user_id, 'disconnected')

    def disconnect_no_action(self, user_id):
        self.dao.user.disconnect(user_id)
        self.set_presence(user_id, 'disconnected', action=False)

    def set_presence(self, user_id, presence, action=True):
        user_profile = self.dao.user.get_cti_profile_id(user_id)
        if self.presence_service_manager.is_valid_presence(user_profile, presence):
            self.dao.user.set_presence(user_id, presence)
            if action is True:
                self.presence_service_executor.execute_actions(user_id, presence)
            self.user_service_notifier.presence_updated(user_id, presence)
            agent_id = self.dao.user.get_agent_id(user_id)
            if agent_id is not None:
                self.agent_service_manager.set_presence(agent_id, presence)

    def pickup_the_phone(self, client_connection):
        client_connection.answer_cb()

    def enable_recording(self, target):
        user_db.enable_service(target, 'callrecord')
        self.user_service_notifier.recording_enabled(target)

    def disable_recording(self, target):
        user_db.disable_service(target, 'callrecord')
        self.user_service_notifier.recording_disabled(target)

    def _dial(self, user_id, exten):
        try:
            line = self.dao.user.get_line(user_id)
            fullname = self.dao.user.get_fullname(user_id)
        except LookupError:
            logger.warning('Failed to dial %s for user %s', exten, user_id)
        else:
            return self.ami_class.originate(
                line['protocol'],
                line['name'],
                line['number'],
                fullname,
                exten,
                exten,
                line['context'],
            )

    def _register_originate_response_callback(self, action_id, client_connection, user_id, exten):
        callback = partial(self._on_originate_response_callback, client_connection, user_id, exten)
        AMIResponseHandler.get_instance().register_callback(action_id, callback)

    def _on_originate_response_callback(self, client_connection, user_id, exten, result):
        response = result.get(RESPONSE)
        if response == SUCCESS:
            line = self.dao.user.get_line(user_id)
            self._on_originate_success(client_connection, exten, line)
        else:
            self._on_originate_error(client_connection, user_id, exten, result.get(MESSAGE))

    def _on_originate_success(self, client_connection, exten, line):
        interface = '%(protocol)s/%(name)s' % line
        self._call_manager.answer_next_ringing_call(client_connection, interface)
        client_connection.send_message(CTIMessageFormatter.dial_success(exten))

    def _on_originate_error(self, client_connection, user_id, exten, message):
        logger.warning('Originate failed from user %s to %s: %s', user_id, exten, message)
        formatted_msg = CTIMessageFormatter.ipbxcommand_error('unreachable_extension:%s' % exten)
        client_connection.send_message(formatted_msg)

    def deliver_dnd_message(self, user_uuid, enabled):
        try:
            user_id = str(dao.user.get_by_uuid(user_uuid)['id'])
            self.dao.user.set_dnd(user_id, enabled)
            self.user_service_notifier.dnd_enabled(user_id, enabled)
            self.funckey_manager.dnd_in_use(user_id, enabled)
        except NoSuchUserException:
            logger.info('received a %s dnd event on an unknown user %s', enabled, user_uuid)

    def deliver_incallfilter_message(self, user_uuid, enabled):
        try:
            user_id = str(dao.user.get_by_uuid(user_uuid)['id'])
            self.dao.user.set_incallfilter(user_id, enabled)
            self.user_service_notifier.incallfilter_enabled(user_id, enabled)
            self.funckey_manager.call_filter_in_use(user_id, enabled)
        except NoSuchUserException:
            logger.info('received a %s incallfilter event on an unknown user %s', enabled, user_uuid)

    def deliver_busy_message(self, user_uuid, enabled, destination):
        try:
            user_id = str(dao.user.get_by_uuid(user_uuid)['id'])
            self.dao.user.set_busy_fwd(user_id, enabled, destination)
            self.user_service_notifier.busy_fwd_enabled(user_id, enabled, destination)
            self.funckey_manager.disable_all_busy_fwd(user_id)

            if not enabled:
                return
            self.funckey_manager.busy_fwd_in_use(user_id, '', enabled)
            destinations = self.dao.forward.busy_destinations(user_id)
            if destination in destinations:
                self.funckey_manager.busy_fwd_in_use(user_id, destination, enabled)

        except NoSuchUserException:
            logger.info('received a %s busy forward event on an unknown user %s', enabled, user_uuid)

    def deliver_rna_message(self, user_uuid, enabled, destination):
        try:
            user_id = str(dao.user.get_by_uuid(user_uuid)['id'])
            self.dao.user.set_rna_fwd(user_id, enabled, destination)
            self.user_service_notifier.rna_fwd_enabled(user_id, enabled, destination)

            self.funckey_manager.disable_all_rna_fwd(user_id)
            if not enabled:
                return
            self.funckey_manager.rna_fwd_in_use(user_id, '', enabled)
            destinations = self.dao.forward.rna_destinations(user_id)
            if destination in destinations:
                self.funckey_manager.rna_fwd_in_use(user_id, destination, enabled)

        except NoSuchUserException:
            logger.info('received a %s rna forward event on an unknown user %s', enabled, user_uuid)

    def deliver_unconditional_message(self, user_uuid, enabled, destination):
        try:
            user_id = str(dao.user.get_by_uuid(user_uuid)['id'])
            self.dao.user.set_unconditional_fwd(user_id, enabled, destination)
            self.user_service_notifier.unconditional_fwd_enabled(user_id, enabled, destination)

            self.funckey_manager.disable_all_unconditional_fwd(user_id)
            if not enabled:
                return
            self.funckey_manager.unconditional_fwd_in_use(user_id, '', enabled)
            destinations = self.dao.forward.unc_destinations(user_id)
            if destination in destinations:
                self.funckey_manager.unconditional_fwd_in_use(user_id, destination, enabled)

        except NoSuchUserException:
            logger.info('received a %s unconditional forward event on an unknown user %s', enabled, user_uuid)

    def _async_set_service(self, user_id, service, enabled):
        self._runner.run(self._client.users(user_id).update_service,
                         service_name=service,
                         service={'enabled': enabled})

    def _async_set_forward(self, user_id, forward, enabled, destination):
        self._runner.run(self._client.users(user_id).update_forward,
                         forward_name=forward,
                         forward={'enabled': enabled,
                                  'destination': destination})

    @bus_listener_thread
    @ack_bus_message
    def _on_bus_services_message_event(self, event):
        data = event.get('data', {})
        try:
            user_uuid = data['user_uuid']
            enabled = data['enabled']
            name = event['name']
        except KeyError as e:
            logger.info('_on_bus_services_message_event: received an incomplete dnd message event: %s', e)

        if name == 'users_services_dnd_updated':
            self._task_queue.put(self.deliver_dnd_message, user_uuid, enabled)
        elif name == 'users_services_incallfilter_updated':
            self._task_queue.put(self.deliver_incallfilter_message, user_uuid, enabled)

    @bus_listener_thread
    @ack_bus_message
    def _on_bus_forwards_message_event(self, event):
        data = event.get('data', {})
        try:
            user_uuid = data['user_uuid']
            enabled = data['enabled']
            destination = data['destination']
            name = event['name']
        except KeyError as e:
            logger.info('_on_bus_services_message_event: received an incomplete dnd message event: %s', e)

        if name == 'users_forwards_busy_updated':
            self._task_queue.put(self.deliver_busy_message, user_uuid, enabled, destination)
        elif name == 'users_forwards_noanswer_updated':
            self._task_queue.put(self.deliver_rna_message, user_uuid, enabled, destination)
        elif name == 'users_forwards_unconditional_updated':
            self._task_queue.put(self.deliver_unconditional_message, user_uuid, enabled, destination)
