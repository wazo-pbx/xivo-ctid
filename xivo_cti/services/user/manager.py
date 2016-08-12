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

from xivo_bus import Marshaler
from xivo_bus.resources.cti.event import UserStatusUpdateEvent
from xivo_confd_client import Client as ConfdClient

from xivo_cti import dao
from xivo_cti import config
from xivo_cti.bus_listener import bus_listener_thread, ack_bus_message
from xivo_cti.database import user_db
from xivo_cti.exception import NoSuchUserException

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
                 async_runner,
                 bus_listener,
                 bus_publisher,
                 task_queue):
        self.user_service_notifier = user_service_notifier
        self.agent_service_manager = agent_service_manager
        self.presence_service_manager = presence_service_manager
        self.funckey_manager = funckey_manager
        self.dao = dao
        self._runner = async_runner
        self._task_queue = task_queue
        self._bus_publisher = bus_publisher
        services_routing_key = 'config.users.*.services.*.updated'
        bus_listener.add_callback(services_routing_key, self._on_bus_services_message_event)

        forwards_routing_key = 'config.users.*.forwards.*.updated'
        bus_listener.add_callback(forwards_routing_key, self._on_bus_forwards_message_event)
        bus_listener.add_callback(UserStatusUpdateEvent.routing_key, self._on_bus_user_status_update_event)

    def connect(self, user_id, user_uuid, auth_token, state):
        self.dao.user.connect(user_id)
        self.send_presence(user_uuid, state)

    def enable_dnd(self, user_uuid, auth_token):
        logger.debug('Enable DND called for user_uuid %s', user_uuid)
        self._async_set_service(user_uuid, auth_token, 'dnd', True)

    def disable_dnd(self, user_uuid, auth_token):
        logger.debug('Disable DND called for user_uuid %s', user_uuid)
        self._async_set_service(user_uuid, auth_token, 'dnd', False)

    def set_dnd(self, user_uuid, auth_token, status):
        self.enable_dnd(user_uuid, auth_token) if status else self.disable_dnd(user_uuid, auth_token)

    def enable_filter(self, user_uuid, auth_token):
        logger.debug('Enable IncallFilter called for user_uuid %s', user_uuid)
        self._async_set_service(user_uuid, auth_token, 'incallfilter', True)

    def disable_filter(self, user_uuid, auth_token):
        logger.debug('Disable IncallFilter called for user_uuid %s', user_uuid)
        self._async_set_service(user_uuid, auth_token, 'incallfilter', False)

    def enable_unconditional_fwd(self, user_uuid, auth_token, destination):
        if not destination:
            self.disable_unconditional_fwd(user_uuid, auth_token, destination)
            return
        logger.debug('Enable Unconditional called for user_uuid %s', user_uuid)
        self._async_set_forward(user_uuid, auth_token, 'unconditional', True, destination)

    def disable_unconditional_fwd(self, user_uuid, auth_token, destination):
        logger.debug('Disable Unconditional called for user_uuid %s', user_uuid)
        self._async_set_forward(user_uuid, auth_token, 'unconditional', False, destination)

    def enable_rna_fwd(self, user_uuid, auth_token, destination):
        if not destination:
            self.disable_rna_fwd(user_uuid, auth_token, destination)
            return
        logger.debug('Enable NoAnswer called for user_uuid %s', user_uuid)
        self._async_set_forward(user_uuid, auth_token, 'noanswer', True, destination)

    def disable_rna_fwd(self, user_uuid, auth_token, destination):
        logger.debug('Disable NoAnswer called for user_uuid %s', user_uuid)
        self._async_set_forward(user_uuid, auth_token, 'noanswer', False, destination)

    def enable_busy_fwd(self, user_uuid, auth_token, destination):
        if not destination:
            self.disable_busy_fwd(user_uuid, auth_token, destination)
            return
        logger.debug('Enable Busy called for user_uuid %s', user_uuid)
        self._async_set_forward(user_uuid, auth_token, 'busy', True, destination)

    def disable_busy_fwd(self, user_uuid, auth_token, destination):
        logger.debug('Disable Busy called for user_uuid %s', user_uuid)
        self._async_set_forward(user_uuid, auth_token, 'busy', False, destination)

    def disconnect(self, user_id, user_uuid):
        self.dao.user.disconnect(user_id)
        self.send_presence(user_uuid, 'disconnected')

    def disconnect_no_action(self, user_id, user_uuid):
        self.dao.user.disconnect(user_id)
        self.set_presence(user_id, user_uuid, None, 'disconnected', action=False)

    def _on_new_presence(self, user_uuid, presence):
        try:
            user_id = str(self.dao.user.get(user_uuid)['id'])
        except NoSuchUserException:
            logger.info('received a presence from an unknown user %s', user_uuid)
        else:
            auth_token = config['auth']['token']
            self.set_presence(user_id, user_uuid, auth_token, presence)

    def set_presence(self, user_id, user_uuid, auth_token, presence, action=True):
        user_profile = self.dao.user.get_cti_profile_id(user_id)
        if self.presence_service_manager.is_valid_presence(user_profile, presence):
            self.dao.user.set_presence(user_id, presence)
            if action is True:
                self.presence_service_executor.execute_actions(user_id, user_uuid, auth_token, presence)
            self.user_service_notifier.presence_updated(user_id, presence)
            agent_id = self.dao.user.get_agent_id(user_id)
            if agent_id is not None:
                self.agent_service_manager.set_presence(agent_id, presence)

    def send_presence(self, user_uuid, presence):
        self._bus_publisher.publish(UserStatusUpdateEvent(user_uuid, presence))

    def pickup_the_phone(self, client_connection):
        client_connection.answer_cb()

    def enable_recording(self, target):
        user_db.enable_service(target, 'callrecord')
        self.user_service_notifier.recording_enabled(target)

    def disable_recording(self, target):
        user_db.disable_service(target, 'callrecord')
        self.user_service_notifier.recording_disabled(target)

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
            self.funckey_manager.update_all_busy_fwd(user_id, enabled, destination)
        except NoSuchUserException:
            logger.info('received a %s busy forward event on an unknown user %s', enabled, user_uuid)

    def deliver_rna_message(self, user_uuid, enabled, destination):
        try:
            user_id = str(dao.user.get_by_uuid(user_uuid)['id'])
            self.dao.user.set_rna_fwd(user_id, enabled, destination)
            self.user_service_notifier.rna_fwd_enabled(user_id, enabled, destination)
            self.funckey_manager.update_all_rna_fwd(user_id, enabled, destination)
        except NoSuchUserException:
            logger.info('received a %s rna forward event on an unknown user %s', enabled, user_uuid)

    def deliver_unconditional_message(self, user_uuid, enabled, destination):
        try:
            user_id = str(dao.user.get_by_uuid(user_uuid)['id'])
            self.dao.user.set_unconditional_fwd(user_id, enabled, destination)
            self.user_service_notifier.unconditional_fwd_enabled(user_id, enabled, destination)
            self.funckey_manager.update_all_unconditional_fwd(user_id, enabled, destination)
        except NoSuchUserException:
            logger.info('received a %s unconditional forward event on an unknown user %s', enabled, user_uuid)

    def _async_set_service(self, user_uuid, auth_token, service, enabled):
        client = ConfdClient(token=auth_token, **config['confd'])
        self._runner.run(client.users(user_uuid).update_service,
                         service_name=service,
                         service={'enabled': enabled})

    def _async_set_forward(self, user_uuid, auth_token, forward, enabled, destination):
        client = ConfdClient(token=auth_token, **config['confd'])
        self._runner.run(client.users(user_uuid).update_forward,
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

    @bus_listener_thread
    @ack_bus_message
    def _on_bus_user_status_update_event(self, body):
        try:
            event = Marshaler.unmarshal_message(body, UserStatusUpdateEvent)
        except KeyError as e:
            logger.info('_on_bus_user_status_update_event: received an incomplete event: %s', e)
        else:
            self._task_queue.put(self._on_new_presence, event.id_, event.status)
