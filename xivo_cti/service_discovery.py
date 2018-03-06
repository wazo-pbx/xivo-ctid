# -*- coding: utf-8 -*-
# Copyright (C) 2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

import requests

from socket import socket, error as socket_error

from xivo_cti.http_app import HTTPInterface


# this function is not executed from the main thread
def self_check(config):
    host = 'localhost'
    http_port = config['rest_api']['http']['port']
    cti_port = config['client']['port']
    info_url = 'http://{}:{}/{}/infos'.format(host, http_port, HTTPInterface.VERSION)

    try:
        http_up = requests.get(info_url).status_code == 200
    except Exception:
        return False

    s = socket()
    try:
        s.connect((host, cti_port))
        cti_up = True
    except socket_error:
        return False
    finally:
        s.close()

    return http_up and cti_up
