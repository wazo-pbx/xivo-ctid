# -*- coding: utf-8 -*-
# Copyright 2007-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from __future__ import print_function

import argparse
import logging
import time
import xivo_cti

from xivo.chain_map import ChainMap
from xivo.config_helper import parse_config_file, read_config_file_hierarchy

from xivo_dao.helpers.db_utils import session_scope
from xivo_dao import (cti_service_dao, cti_preference_dao, cti_profile_dao,
                      cti_main_dao, cti_phonehints_dao,
                      cti_userstatus_dao, cti_sheets_dao)

logger = logging.getLogger('cti_config')

_default_config = {
    'debug': False,
    'foreground': False,
    'pidfile': '/var/run/xivo-ctid/%s.pid' % xivo_cti.DAEMONNAME,
    'logfile': '/var/log/%s.log' % xivo_cti.DAEMONNAME,
    'db_uri': 'postgresql://asterisk:proformatique@localhost/asterisk',
    'config_file': '/etc/xivo-ctid/config.yml',
    'extra_config_files': '/etc/xivo-ctid/conf.d/',
    'user': 'xivo-ctid',
    'socket_timeout': 10,
    'client': {
        'listen': '0.0.0.0',
        'port': 5003,
        'login_timeout': 5,
        'enabled': True,
    },
    'info': {
        'listen': '127.0.0.1',
        'port': 5005,
        'enabled': True,
    },
    'update_events_socket': {
        'listen': '127.0.0.1',
        'port': 5004,
        'enabled': True,
    },
    'main': {
        'certfile': '/usr/share/xivo-certs/server.crt',
        'keyfile': '/usr/share/xivo-certs/server.key',
    },
    'agentd': {
        'host': 'localhost',
        'timeout': 3,
        'verify_certificate': '/usr/share/xivo-certs/server.crt',
    },
    'auth': {
        'host': 'localhost',
        'port': 9497,
        'timeout': 3,
        'key_file': '/var/lib/wazo-auth-keys/xivo-ctid-key.yml',
        'verify_certificate': '/usr/share/xivo-certs/server.crt',
        'backend': 'wazo_user',
    },
    'bus': {
        'exchange_name': 'xivo',
        'exchange_type': 'topic'
    },
    'ctid_ng': {
        'host': 'localhost',
        'port': 9500,
        'verify_certificate': '/usr/share/xivo-certs/server.crt',
    },
    'confd': {
        'host': 'localhost',
        'port': 9486,
        'version': 1.1,
        'verify_certificate': '/usr/share/xivo-certs/server.crt',
    },
    'dird': {
        'host': 'localhost',
        'port': 9489,
        'version': 0.1,
        'verify_certificate': '/usr/share/xivo-certs/server.crt',
    },
    'provd': {
        'host': 'localhost',
        'port': 8666,
        'prefix': '/provd',
        'verify_certificate': '/usr/share/xivo-certs/server.crt',
    },
    'service_discovery': {
        'enabled': True,
        'advertise_address': 'localhost',
        'advertise_port': 9495,
        'advertise_address_interface': 'eth0',
        'refresh_interval': 25,
        'retry_interval': 2,
        'ttl_interval': 30,
        'extra_tags': [],
    },
    'switchboard_polycom': {
        'username': 'xivo_switchboard',
        'password': 'xivo_switchboard',
        'answer_delay': 0.4,
    },
    'switchboard_snom': {
        'username': 'guest',
        'password': 'guest',
        'answer_delay': 0.5,
    },
    'switchboard_queues': {
        '__switchboard': True,
    },
    'switchboard_hold_queues': {
        '__switchboard_hold': True,
    },
    'ami': {
        'host': 'localhost',
        'port': 5038,
        'username': 'xivo_cti_user',
        'password': 'phaickbebs9',
    },
}
_cli_config = {}
_db_config = {}
_file_config = {}
_auth_config = {}


def init_auth_config():
    global _auth_config

    key_file = parse_config_file(xivo_cti.config['auth']['key_file'])
    _auth_config = {'auth': {'service_id': key_file['service_id'],
                             'service_key': key_file['service_key']}}
    _update_config()


def on_token_change(token_id):
    _auth_config['auth']['token'] = token_id

    _update_config()


def init_config_file():
    global _file_config

    _file_config = read_config_file_hierarchy(xivo_cti.config)

    _update_config()


def init_cli_config(args):
    parser = _new_parser()
    parsed_args = parser.parse_args(args)
    _process_parsed_args(parsed_args)
    _update_config()


def update_db_config():
    global _db_config

    db_config = _DbConfig()
    db_config.update()
    _db_config = db_config.getconfig()
    _update_config()


def _new_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', action='store_true')
    parser.add_argument('-f', '--foreground', action='store_true')
    parser.add_argument('-p', '--pidfile')
    parser.add_argument('-l', '--logfile')
    parser.add_argument('-c', '--config-file')
    return parser


def _process_parsed_args(parsed_args):
    if parsed_args.debug:
        _cli_config['debug'] = parsed_args.debug
    if parsed_args.foreground:
        _cli_config['foreground'] = parsed_args.foreground
    if parsed_args.pidfile:
        _cli_config['pidfile'] = parsed_args.pidfile
    if parsed_args.logfile:
        _cli_config['logfile'] = parsed_args.logfile
    if parsed_args.config_file:
        _cli_config['config_file'] = parsed_args.config_file


class _DbConfig(object):

    def __init__(self):
        self.xc_json = {}

    def update(self):
        start_time = time.time()
        self.fill_conf()
        logger.info('Config successfully updated in %.6f seconds', (time.time() - start_time))

    def fill_conf(self):
        with session_scope():
            self.xc_json.update(cti_main_dao.get_config())
            self.xc_json['phonestatus'] = cti_phonehints_dao.get_config()
            self.xc_json['userstatus'] = cti_userstatus_dao.get_config()
            self.xc_json['sheets'] = cti_sheets_dao.get_config()
            self.xc_json['profiles'] = self._get_profiles()
            self.xc_json['services'] = self._get_services()
            self.xc_json['preferences'] = self._get_preferences()

    def _get_profiles(self):
        profiles = cti_profile_dao.get_profiles()
        res = {}
        for profile_key, profile_value in profiles.iteritems():
            new_profile = profile_value
            if 'xlets' in profile_value:
                new_xlet_list = []
                for xlet in profile_value['xlets']:
                    new_xlet = [xlet['name'], xlet['layout']]
                    if xlet['layout'] == 'dock':
                        args = ''
                        args += 'f' if xlet['floating'] else ''
                        args += 'c' if xlet['closable'] else ''
                        args += 'm' if xlet['movable'] else ''
                        args += 's' if xlet['scrollable'] else ''
                        new_xlet.append(args)
                    if xlet['order']:
                        new_xlet.append(str(xlet['order']))
                    new_xlet_list.append(new_xlet)
                    new_profile['xlets'] = new_xlet_list
            res[profile_key] = new_profile
        return res

    def _get_services(self):
        services = cti_service_dao.get_services()
        res = {}
        for service_key, service_value in services.iteritems():
            new_service_key = 'itm_services_%s' % service_key
            new_service_value = [''] if not service_value else service_value
            res[new_service_key] = new_service_value
        return res

    def _get_preferences(self):
        preferences = cti_preference_dao.get_preferences()
        res = {}
        for preference_key, preference_value in preferences.iteritems():
            new_preference_key = 'itm_preferences_%s' % preference_key
            new_preference_value = False if not preference_value else preference_value
            res[new_preference_key] = new_preference_value
        return res

    def getconfig(self):
        return self.xc_json


def _update_config():
    xivo_cti.config.data = ChainMap(_cli_config, _auth_config, _file_config, _db_config, _default_config)
