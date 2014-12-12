# -*- coding: utf-8 -*-

# Copyright (C) 2014 Avencall
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


class NoSuchPhoneException(LookupError):

    def __init__(self, phone_id):
        msg = 'No phone matching id {type}({value})'.format(
            type=type(phone_id).__name__, value=phone_id)
        super(NoSuchPhoneException, self).__init__(msg)


class PhoneDAO(object):

    def __init__(self, innerdata):
        self._innerdata = innerdata

    def get_status(self, phone_id):
        if phone_id not in self._innerdata.xod_status['phones']:
            raise NoSuchPhoneException(phone_id)

        return self._innerdata.xod_status['phones'][phone_id]['hintstatus']

    def update_status(self, phone_id, status):
        current_status = self.get_status(phone_id)
        self._innerdata.xod_status['phones'][phone_id]['hintstatus'] = status
        return current_status != status
