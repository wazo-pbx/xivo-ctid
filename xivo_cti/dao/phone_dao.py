# -*- coding: utf-8 -*-
# Copyright (C) 2014-2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo.asterisk.protocol_interface import protocol_interfaces_from_hint

from xivo_cti.exception import NoSuchPhoneException


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

    def get_phone_ids_from_hint(self, hint):
        for protocol, interface in protocol_interfaces_from_hint(hint.lower()):
            phone_id = self._innerdata.xod_config['phones'].get_phone_id_from_proto_and_name(protocol, interface)
            if phone_id is not None:
                yield phone_id
