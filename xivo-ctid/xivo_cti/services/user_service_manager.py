# -*- coding: UTF-8 -*-

# XiVO CTI Server
# Copyright (C) 2009-2011  Avencall
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

    def enable_dnd(self, user_id):
        self.user_features_dao.enable_dnd(user_id)
        self.user_service_notifier.dnd_enabled(user_id)
        self.funckey_manager.dnd_in_use(user_id, True)

    def disable_dnd(self, user_id):
        self.user_features_dao.disable_dnd(user_id)
        self.user_service_notifier.dnd_disabled(user_id)
        self.funckey_manager.dnd_in_use(user_id, False)

    def enable_filter(self, user_id):
        self.user_features_dao.enable_filter(user_id)
        self.user_service_notifier.filter_enabled(user_id)
        self.funckey_manager.call_filter_in_use(user_id, True)

    def disable_filter(self, user_id):
        self.user_features_dao.disable_filter(user_id)
        self.user_service_notifier.filter_disabled(user_id)
        self.funckey_manager.call_filter_in_use(user_id, False)

    def enable_unconditional_fwd(self, user_id, destination):
        self.user_features_dao.enable_unconditional_fwd(user_id, destination)
        self.user_service_notifier.unconditional_fwd_enabled(user_id, destination)
        self.funckey_manager.unconditional_fwd_in_use(user_id, destination, True)

    def disable_unconditional_fwd(self, user_id, destination):
        self.user_features_dao.disable_unconditional_fwd(user_id, destination)
        self.user_service_notifier.unconditional_fwd_disabled(user_id, destination)
        key_dest = self.phone_funckey_dao.get_dest_unc(user_id)
        self.funckey_manager.unconditional_fwd_in_use(user_id, key_dest, False)

    def enable_rna_fwd(self, user_id, destination):
        self.user_features_dao.enable_rna_fwd(user_id, destination)
        self.user_service_notifier.rna_fwd_enabled(user_id, destination)
        self.funckey_manager.rna_fwd_in_use(user_id, destination, True)

    def disable_rna_fwd(self, user_id, destination):
        self.user_features_dao.disable_rna_fwd(user_id, destination)
        self.user_service_notifier.rna_fwd_disabled(user_id, destination)
        key_dest = self.phone_funckey_dao.get_dest_rna(user_id)
        self.funckey_manager.rna_fwd_in_use(user_id, key_dest, False)

    def enable_busy_fwd(self, user_id, destination):
        self.user_features_dao.enable_busy_fwd(user_id, destination)
        self.user_service_notifier.busy_fwd_enabled(user_id, destination)

    def disable_busy_fwd(self, user_id, destination):
        self.user_features_dao.disable_busy_fwd(user_id, destination)
        self.user_service_notifier.busy_fwd_disabled(user_id, destination)
