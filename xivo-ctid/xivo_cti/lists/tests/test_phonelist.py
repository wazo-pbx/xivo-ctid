# -*- coding: utf-8 -*-

# Copyright (C) 2007-2013 Avencall
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

import unittest
from xivo_cti.lists.cti_phonelist import PhoneList


class Test(unittest.TestCase):

    PHONE_1 = {'protocol': 'sip',
              'buggymwi': None,
              'amaflags': 'default',
              'sendrpid': None,
              'videosupport': None,
              'regseconds': '0',
              'maxcallbitrate': None,
              'registertrying': None,
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
              'rules_type': '',
              'call-limit': '10',
              'num': 1,
              'initialized': False,
              'progressinband': None,
              'port': None,
              'transport': None,
              'category': 'user',
              'md5secret': '',
              'regserver': None,
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
              'rules_time': '30',
              'callerid': '"User2" <102>',
              'line_num': 0,
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
              'rules_group': '',
              'rfc2833compensate': None,
              'g726nonstandard': None,
              'contactdeny': None,
              'iduserfeatures': 11,
              'snom_aoc_enabled': None,
              'fullname': None,
              'rules_order': 1,
              't38pt_udptl': None,
              'subscribemwi': '0',
              'mohsuggest': None,
              'id': 19,
              'autoframing': None,
              't38pt_usertpsource': None,
              'ipaddr': '',
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
              'lastms': '',
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
              'regseconds': '0',
              'maxcallbitrate': None,
              'registertrying': None,
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
              'rules_type': '',
              'call-limit': '10',
              'num': 1,
              'initialized': False,
              'progressinband': None,
              'port': None,
              'transport': None,
              'category': 'user',
              'md5secret': '',
              'regserver': None,
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
              'rules_time': '30',
              'callerid': '"User2" <102>',
              'line_num': 0,
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
              'rules_group': '',
              'rfc2833compensate': None,
              'g726nonstandard': None,
              'contactdeny': None,
              'iduserfeatures': 11,
              'snom_aoc_enabled': None,
              'fullname': None,
              'rules_order': 2,  # phone order
              't38pt_udptl': None,
              'subscribemwi': '0',
              'mohsuggest': None,
              'id': 21,
              'autoframing': None,
              't38pt_usertpsource': None,
              'ipaddr': '',
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
              'lastms': '',
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
              'regseconds': '0',
              'maxcallbitrate': None,
              'registertrying': None,
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
              'rules_type': '',
              'call-limit': '10',
              'num': 1,
              'initialized': False,
              'progressinband': None,
              'port': None,
              'transport': None,
              'category': 'user',
              'md5secret': '',
              'regserver': None,
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
              'rules_time': '30',
              'callerid': '"User3" <102>',
              'line_num': 0,
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
              'rules_group': '',
              'rfc2833compensate': None,
              'g726nonstandard': None,
              'contactdeny': None,
              'iduserfeatures': 11,
              'snom_aoc_enabled': None,
              'fullname': None,
              'rules_order': 2,  # phone order
              't38pt_udptl': None,
              'subscribemwi': '0',
              'mohsuggest': None,
              'id': 22,
              'autoframing': None,
              't38pt_usertpsource': None,
              'ipaddr': '',
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
              'lastms': '',
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
        self.phone_list = PhoneList()
        self.phone_list.keeplist = self.keeplist
        self.phone_list._update_lookup_dictionaries()

    def test_find_phone_by_channel_no_result(self):
        channel = 'SIP/k8fh45-000000023'

        phone = self.phone_list.find_phone_by_channel(channel)

        self.assertEqual(phone, None)

    def test_find_phone_by_channel_sip(self):
        channel = 'SIP/yp0ra4-000000023'

        phone = self.phone_list.find_phone_by_channel(channel)

        self.assertEqual(phone, self.PHONE_2)

    def test_find_phone_by_channel_sccp(self):
        channel = 'sccp/102@SEP004F3355A2FF'

        phone = self.phone_list.find_phone_by_channel(channel)

        self.assertEqual(phone, self.PHONE_3)

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
