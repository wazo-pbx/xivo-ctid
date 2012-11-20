# -*- coding: utf-8 -*-

# XiVO CTI Server
# Copyright (C) 2009-2012  Avencall
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


class UserServiceManager(object):

    def __init__(self,
                 user_service_notifier,
                 agent_service_manager,
                 presence_service_manager,
                 funckey_manager,
                 user_features_dao,
                 phone_funckey_dao,
                 line_features_dao):
        self.user_service_notifier = user_service_notifier
        self.agent_service_manager = agent_service_manager
        self.presence_service_manager = presence_service_manager
        self.funckey_manager = funckey_manager
        self.user_features_dao = user_features_dao
        self.phone_funckey_dao = phone_funckey_dao
        self.line_features_dao = line_features_dao

    def enable_dnd(self, user_id):
        self.user_features_dao.enable_dnd(user_id)
        self.user_service_notifier.dnd_enabled(user_id)
        self.funckey_manager.dnd_in_use(user_id, True)

    def disable_dnd(self, user_id):
        self.user_features_dao.disable_dnd(user_id)
        self.user_service_notifier.dnd_disabled(user_id)
        self.funckey_manager.dnd_in_use(user_id, False)

    def set_dnd(self, user_id, status):
        self.enable_dnd(user_id) if status else self.disable_dnd(user_id)

    def enable_filter(self, user_id):
        self.user_features_dao.enable_filter(user_id)
        self.user_service_notifier.filter_enabled(user_id)
        self.funckey_manager.call_filter_in_use(user_id, True)

    def disable_filter(self, user_id):
        self.user_features_dao.disable_filter(user_id)
        self.user_service_notifier.filter_disabled(user_id)
        self.funckey_manager.call_filter_in_use(user_id, False)

    def enable_unconditional_fwd(self, user_id, destination):
        if destination == '':
            self.disable_unconditional_fwd(user_id, destination)
            return
        self.user_features_dao.enable_unconditional_fwd(user_id, destination)
        self.user_service_notifier.unconditional_fwd_enabled(user_id, destination)
        self.funckey_manager.disable_all_unconditional_fwd(user_id)
        destinations = self.phone_funckey_dao.get_dest_unc(user_id)
        self.funckey_manager.unconditional_fwd_in_use(user_id, '', True)
        if destination in destinations:
            self.funckey_manager.unconditional_fwd_in_use(user_id, destination, True)

    def disable_unconditional_fwd(self, user_id, destination):
        self.user_features_dao.disable_unconditional_fwd(user_id, destination)
        self.user_service_notifier.unconditional_fwd_disabled(user_id, destination)
        self.funckey_manager.disable_all_unconditional_fwd(user_id)

    def enable_rna_fwd(self, user_id, destination):
        self.user_features_dao.enable_rna_fwd(user_id, destination)
        self.user_service_notifier.rna_fwd_enabled(user_id, destination)
        self.funckey_manager.disable_all_rna_fwd(user_id)
        if destination in self.phone_funckey_dao.get_dest_rna(user_id):
            self.funckey_manager.rna_fwd_in_use(user_id, destination, True)

    def disable_rna_fwd(self, user_id, destination):
        self.user_features_dao.disable_rna_fwd(user_id, destination)
        self.user_service_notifier.rna_fwd_disabled(user_id, destination)
        self.funckey_manager.disable_all_rna_fwd(user_id)

    def enable_busy_fwd(self, user_id, destination):
        self.user_features_dao.enable_busy_fwd(user_id, destination)
        self.user_service_notifier.busy_fwd_enabled(user_id, destination)
        self.funckey_manager.disable_all_busy_fwd(user_id)
        if destination in self.phone_funckey_dao.get_dest_busy(user_id):
            self.funckey_manager.busy_fwd_in_use(user_id, destination, True)

    def disable_busy_fwd(self, user_id, destination):
        self.user_features_dao.disable_busy_fwd(user_id, destination)
        self.user_service_notifier.busy_fwd_disabled(user_id, destination)
        self.funckey_manager.disable_all_busy_fwd(user_id)

    def disconnect(self, user_id):
        self.user_features_dao.disconnect(user_id)
        self.set_presence(user_id, 'disconnected')

    def disconnect_no_action(self, user_id):
        self.user_features_dao.disconnect(user_id)
        self.set_presence(user_id, 'disconnected', action=False)

    def set_presence(self, user_id, presence, action=True):
        user_profile = self.user_features_dao.get_profile(user_id)
        if self.presence_service_manager.is_valid_presence(user_profile, presence):
            self.user_features_dao.set_presence(user_id, presence)
            if action is True:
                self.presence_service_executor.execute_actions(user_id, presence)
            self.user_service_notifier.presence_updated(user_id, presence)
            if self.user_features_dao.is_agent(user_id):
                agent_id = self.user_features_dao.agent_id(user_id)
                self.agent_service_manager.set_presence(agent_id, presence)

    def get_context(self, user_id):
        return self.line_features_dao.find_context_by_user_id(user_id)
