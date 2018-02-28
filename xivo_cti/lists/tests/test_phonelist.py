# -*- coding: utf-8 -*-
# Copyright (C) 2007-2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

import unittest
from xivo_cti.lists.phones_list import PhonesList
from mock import Mock
from mock import patch
from xivo.asterisk.protocol_interface import InvalidChannelError
from xivo_cti.innerdata import Safe
from xivo_cti.ctiserver import CTIServer


class TestPhoneList(unittest.TestCase):

    PHONE_1 = {'protocol': 'sip',
               'buggymwi': None,
               'amaflags': 'default',
               'sendrpid': None,
               'videosupport': None,
               'maxcallbitrate': None,
               'session-minse': None,
               'maxforwards': None,
               'internal': False,
               'rtpholdtimeout': None,
               'session-expires': None,
               'defaultip': None,
               'ignoresdpversion': None,
               'ipfrom': '192.168.32.157',
               'vmexten': None,
               'name': 'bbbaaa',
               'callingpres': None,
               'textsupport': None,
               'unsolicited_mailbox': None,
               'outboundproxy': None,
               'fromuser': None,
               'cid_number': None,
               'commented': False,
               'useclientcode': None,
               'call-limit': '10',
               'num': 1,
               'initialized': False,
               'progressinband': None,
               'port': None,
               'transport': None,
               'category': 'user',
               'md5secret': '',
               'directmedia': None,
               'mailbox': None,
               'qualifyfreq': None,
               'host': 'dynamic',
               'promiscredir': None,
               'disallow': None,
               'allowoverlap': None,
               'accountcode': None,
               'dtmfmode': None,
               'language': 'fr_FR',
               'usereqphone': None,
               'qualify': None,
               'useridentity': 'User2 ',
               'trustrpid': None,
               'context': 'default',
               'timert1': None,
               'session-refresher': None,
               'provisioningid': 152530,
               'mohinterpret': None,
               'allowsubscribe': None,
               'number': '102',
               'session-timers': None,
               'busylevel': None,
               'callcounter': None,
               'callerid': '"User2" <102>',
               'configregistrar': 'default',
               'encryption': False,
               'remotesecret': None,
               'secret': 'XM5Y4J',
               'use_q850_reason': None,
               'type': 'friend',
               'username': None,
               'callbackextension': None,
               'protocolid': 19,
               'disallowed_methods': None,
               'rfc2833compensate': None,
               'g726nonstandard': None,
               'contactdeny': None,
               'iduserfeatures': 11,
               'snom_aoc_enabled': None,
               'fullname': None,
               't38pt_udptl': None,
               'subscribemwi': '0',
               'mohsuggest': None,
               'id': 19,
               'autoframing': None,
               't38pt_usertpsource': None,
               'fromdomain': None,
               'allowtransfer': None,
               'nat': None,
               'config': '',
               'setvar': 'XIVO_USERID=11',
               'contactpermit': None,
               'rtpkeepalive': None,
               'description': '',
               'insecure': None,
               'permit': None,
               'device': '7',
               'subscribecontext': None,
               'regexten': None,
               'identity': 'SIP\\/bbbaaa',
               'deny': None,
               'timerb': None,
               'rtptimeout': None,
               'allow': None}

    PHONE_2 = {'protocol': 'sip',
               'buggymwi': None,
               'amaflags': 'default',
               'sendrpid': None,
               'videosupport': None,
               'maxcallbitrate': None,
               'session-minse': None,
               'maxforwards': None,
               'internal': False,
               'rtpholdtimeout': None,
               'session-expires': None,
               'defaultip': None,
               'ignoresdpversion': None,
               'ipfrom': '192.168.32.157',
               'vmexten': None,
               'name': 'yp0ra4',
               'callingpres': None,
               'textsupport': None,
               'unsolicited_mailbox': None,
               'outboundproxy': None,
               'fromuser': None,
               'cid_number': None,
               'commented': False,
               'useclientcode': None,
               'call-limit': '10',
               'num': 1,
               'initialized': False,
               'progressinband': None,
               'port': None,
               'transport': None,
               'category': 'user',
               'md5secret': '',
               'directmedia': None,
               'mailbox': None,
               'qualifyfreq': None,
               'host': 'dynamic',
               'promiscredir': None,
               'disallow': None,
               'allowoverlap': None,
               'accountcode': None,
               'dtmfmode': None,
               'language': 'fr_FR',
               'usereqphone': None,
               'qualify': None,
               'useridentity': 'User2 ',
               'trustrpid': None,
               'context': 'default',
               'timert1': None,
               'session-refresher': None,
               'provisioningid': 152530,
               'mohinterpret': None,
               'allowsubscribe': None,
               'number': '102',
               'session-timers': None,
               'busylevel': None,
               'callcounter': None,
               'callerid': '"User2" <102>',
               'configregistrar': 'default',
               'encryption': False,
               'remotesecret': None,
               'secret': 'XM5Y4J',
               'use_q850_reason': None,
               'type': 'friend',
               'username': None,
               'callbackextension': None,
               'protocolid': 21,
               'disallowed_methods': None,
               'rfc2833compensate': None,
               'g726nonstandard': None,
               'contactdeny': None,
               'iduserfeatures': 11,
               'snom_aoc_enabled': None,
               'fullname': None,
               't38pt_udptl': None,
               'subscribemwi': '0',
               'mohsuggest': None,
               'id': 21,
               'autoframing': None,
               't38pt_usertpsource': None,
               'fromdomain': None,
               'allowtransfer': None,
               'nat': None,
               'config': '',
               'setvar': 'XIVO_USERID=11',
               'contactpermit': None,
               'rtpkeepalive': None,
               'description': '',
               'insecure': None,
               'permit': None,
               'device': '7',
               'subscribecontext': None,
               'regexten': None,
               'identity': 'SIP\\/yp0ra4',
               'deny': None,
               'timerb': None,
               'rtptimeout': None,
               'allow': None}

    PHONE_3 = {'protocol': 'sccp',
               'buggymwi': None,
               'amaflags': 'default',
               'sendrpid': None,
               'videosupport': None,
               'maxcallbitrate': None,
               'session-minse': None,
               'maxforwards': None,
               'internal': False,
               'rtpholdtimeout': None,
               'session-expires': None,
               'defaultip': None,
               'ignoresdpversion': None,
               'ipfrom': '192.168.32.157',
               'vmexten': None,
               'name': '102',
               'callingpres': None,
               'textsupport': None,
               'unsolicited_mailbox': None,
               'outboundproxy': None,
               'fromuser': None,
               'cid_number': None,
               'commented': False,
               'useclientcode': None,
               'call-limit': '10',
               'num': 1,
               'initialized': False,
               'progressinband': None,
               'port': None,
               'transport': None,
               'category': 'user',
               'md5secret': '',
               'directmedia': None,
               'mailbox': None,
               'qualifyfreq': None,
               'host': 'dynamic',
               'promiscredir': None,
               'disallow': None,
               'allowoverlap': None,
               'accountcode': None,
               'dtmfmode': None,
               'language': 'fr_FR',
               'usereqphone': None,
               'qualify': None,
               'useridentity': 'User3 ',
               'trustrpid': None,
               'context': 'default',
               'timert1': None,
               'session-refresher': None,
               'provisioningid': 152530,
               'mohinterpret': None,
               'allowsubscribe': None,
               'number': '102',
               'session-timers': None,
               'busylevel': None,
               'callcounter': None,
               'callerid': '"User3" <102>',
               'configregistrar': 'default',
               'encryption': False,
               'remotesecret': None,
               'secret': 'XM5Y4J',
               'use_q850_reason': None,
               'type': 'friend',
               'username': None,
               'callbackextension': None,
               'protocolid': 21,
               'disallowed_methods': None,
               'rfc2833compensate': None,
               'g726nonstandard': None,
               'contactdeny': None,
               'iduserfeatures': 11,
               'snom_aoc_enabled': None,
               'fullname': None,
               't38pt_udptl': None,
               'subscribemwi': '0',
               'mohsuggest': None,
               'id': 22,
               'autoframing': None,
               't38pt_usertpsource': None,
               'fromdomain': None,
               'allowtransfer': None,
               'nat': None,
               'config': '',
               'setvar': 'XIVO_USERID=11',
               'contactpermit': None,
               'rtpkeepalive': None,
               'description': '',
               'insecure': None,
               'permit': None,
               'device': '7',
               'subscribecontext': None,
               'regexten': None,
               'identity': 'SIP\\/yp0ra4',
               'deny': None,
               'timerb': None,
               'rtptimeout': None,
               'allow': None}

    keeplist = {PHONE_1['id']: PHONE_1,
                PHONE_2['id']: PHONE_2,
                PHONE_3['id']: PHONE_3}

    def setUp(self):
        innerdata = Mock(Safe)
        innerdata._ctiserver = Mock(CTIServer)
        innerdata.ipbxid = 'xivo'
        self.phone_list = PhonesList(innerdata)
        self.phone_list.keeplist = self.keeplist
        self.phone_list._init_reverse_dictionaries()

    def test_find_phone_by_channel_no_result(self):
        channel = 'SIP/k8fh45-000000023'

        phone = self.phone_list.find_phone_by_channel(channel)

        self.assertEqual(phone, None)

    def test_find_phone_by_channel_sip(self):
        channel = 'SIP/yp0ra4-000000023'

        phone = self.phone_list.find_phone_by_channel(channel)

        self.assertEqual(phone, self.PHONE_2)

    def test_find_phone_by_channel_sccp(self):
        channel = 'SCCP/102-00000000001'

        phone = self.phone_list.find_phone_by_channel(channel)

        self.assertEqual(phone, self.PHONE_3)

    @patch('xivo.asterisk.protocol_interface.protocol_interface_from_channel', Mock(side_effect=InvalidChannelError('test')))
    def test_find_phone_by_channel_invalid(self):
        channel = 'Invalid/102-00000000001'

        phone = self.phone_list.find_phone_by_channel(channel)

        self.assertEqual(phone, None)

    def test_get_user_main_line(self):
        user_id = '11'

        main_line = self.phone_list.get_main_line(user_id)

        self.assertEqual(self.PHONE_1, main_line)

    def test_get_callerid_from_sccp_phone(self):
        self.phone_list.keeplist = {
            '1': {
                'cid_name': 'SccpUser 2',
                'cid_num': '1002',
                'protocol': 'sccp',
            }
        }

        callerid = self.phone_list.get_callerid_from_phone_id('1')

        self.assertEqual('"SccpUser 2" <1002>', callerid)

    def test_get_callerid_from_sip_phone(self):
        self.phone_list.keeplist = {
            '1': {
                'callerid': '"User 1" <1001>',
                'protocol': 'sip',
            }
        }

        callerid = self.phone_list.get_callerid_from_phone_id('1')

        self.assertEqual('"User 1" <1001>', callerid)
