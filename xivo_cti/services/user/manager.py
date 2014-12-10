# -*- coding: utf-8 -*-

# Copyright (C) 2009-2014 Avencall
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

from xivo_cti.ami.ami_response_handler import AMIResponseHandler
from xivo_dao import user_dao
from xivo_dao.data_handler.func_key import services as func_key_services
from xivo_cti import dao
from xivo_cti.model.destination_factory import DestinationFactory
from xivo_cti.cti.cti_message_formatter import CTIMessageFormatter

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
                 call_manager):
        self.user_service_notifier = user_service_notifier
        self.agent_service_manager = agent_service_manager
        self.presence_service_manager = presence_service_manager
        self.funckey_manager = funckey_manager
        self.device_manager = device_manager
        self.dao = dao
        self.ami_class = ami_class
        self._ami_callback_handler = ami_callback_handler
        self._call_manager = call_manager

    def call_destination(self, client_connection, user_id, url_or_exten):
        if DestinationFactory.is_destination_url(url_or_exten):
            exten = DestinationFactory.make_from(url_or_exten).to_exten()
        else:
            exten = url_or_exten

        action_id = self._dial(user_id, exten)
        self._register_originate_response_callback(action_id, client_connection, user_id, exten)

    def enable_dnd(self, user_id):
        self.dao.user.enable_dnd(user_id)
        self.user_service_notifier.dnd_enabled(user_id)
        self.funckey_manager.dnd_in_use(user_id, True)

    def disable_dnd(self, user_id):
        self.dao.user.disable_dnd(user_id)
        self.user_service_notifier.dnd_disabled(user_id)
        self.funckey_manager.dnd_in_use(user_id, False)

    def set_dnd(self, user_id, status):
        self.enable_dnd(user_id) if status else self.disable_dnd(user_id)

    def enable_filter(self, user_id):
        self.dao.user.enable_filter(user_id)
        self.user_service_notifier.filter_enabled(user_id)
        self.funckey_manager.call_filter_in_use(user_id, True)

    def disable_filter(self, user_id):
        self.dao.user.disable_filter(user_id)
        self.user_service_notifier.filter_disabled(user_id)
        self.funckey_manager.call_filter_in_use(user_id, False)

    def enable_unconditional_fwd(self, user_id, destination):
        if destination == '':
            self.disable_unconditional_fwd(user_id, destination)
            return
        self.dao.user.enable_unconditional_fwd(user_id, destination)
        self.user_service_notifier.unconditional_fwd_enabled(user_id, destination)
        self.funckey_manager.disable_all_unconditional_fwd(user_id)
        self.funckey_manager.unconditional_fwd_in_use(user_id, '', True)
        if destination in func_key_services.find_all_fwd_unc(user_id):
            self.funckey_manager.unconditional_fwd_in_use(user_id, destination, True)

    def disable_unconditional_fwd(self, user_id, destination):
        self.dao.user.disable_unconditional_fwd(user_id, destination)
        self.user_service_notifier.unconditional_fwd_disabled(user_id, destination)
        self.funckey_manager.disable_all_unconditional_fwd(user_id)

    def enable_rna_fwd(self, user_id, destination):
        self.dao.user.enable_rna_fwd(user_id, destination)
        self.user_service_notifier.rna_fwd_enabled(user_id, destination)
        self.funckey_manager.disable_all_rna_fwd(user_id)
        if destination in func_key_services.find_all_fwd_rna(user_id):
            self.funckey_manager.rna_fwd_in_use(user_id, destination, True)

    def disable_rna_fwd(self, user_id, destination):
        self.dao.user.disable_rna_fwd(user_id, destination)
        self.user_service_notifier.rna_fwd_disabled(user_id, destination)
        self.funckey_manager.disable_all_rna_fwd(user_id)

    def enable_busy_fwd(self, user_id, destination):
        self.dao.user.enable_busy_fwd(user_id, destination)
        self.user_service_notifier.busy_fwd_enabled(user_id, destination)
        self.funckey_manager.disable_all_busy_fwd(user_id)
        if destination in func_key_services.find_all_fwd_busy(user_id):
            self.funckey_manager.busy_fwd_in_use(user_id, destination, True)

    def disable_busy_fwd(self, user_id, destination):
        self.dao.user.disable_busy_fwd(user_id, destination)
        self.user_service_notifier.busy_fwd_disabled(user_id, destination)
        self.funckey_manager.disable_all_busy_fwd(user_id)

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
            if user_dao.is_agent(user_id):
                agent_id = user_dao.agent_id(user_id)
                self.agent_service_manager.set_presence(agent_id, presence)

    def pickup_the_phone(self, client_connection):
        client_connection.answer_cb()

    def enable_recording(self, target):
        user_dao.enable_recording(target)
        self.user_service_notifier.recording_enabled(target)

    def disable_recording(self, target):
        user_dao.disable_recording(target)
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
