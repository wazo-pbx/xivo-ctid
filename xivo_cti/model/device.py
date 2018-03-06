# -*- coding: utf-8 -*-
# Copyright (C) 2015 Avencall
# SPDX-License-Identifier: GPL-3.0+


class Device(object):

    def __init__(self, id_):
        self.id = id_
        self.ip = None
        self.plugin = None
        self.vendor = None
        self.options = None

    def is_switchboard(self):
        if self.plugin and 'switchboard' in self.plugin:
            return True

        return bool(self.options and self.options.get('switchboard'))

    @classmethod
    def new_from_provd_device(cls, provd_device):
        device = cls(provd_device['id'])
        device.ip = provd_device.get('ip')
        device.plugin = provd_device.get('plugin')
        device.vendor = provd_device.get('vendor')
        device.options = provd_device.get('options')
        return device
