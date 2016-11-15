# -*- coding: utf-8 -*-

# Copyright (C) 2012-2016 Avencall
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

import os
import time

from datetime import datetime
from hamcrest import assert_that
from hamcrest import contains_inanyorder
from hamcrest import equal_to
from hamcrest import empty
from hamcrest import none

from xivo_cti.database import transfer_db as transfer_dao
from xivo_cti.database import user_db as user_dao
from xivo_dao.alchemy.callfilter import Callfilter
from xivo_dao.alchemy.callfiltermember import Callfiltermember
from xivo_dao.alchemy.contextinclude import ContextInclude
from xivo_dao.alchemy.cti_profile import CtiProfile
from xivo_dao.alchemy.ctiphonehintsgroup import CtiPhoneHintsGroup
from xivo_dao.alchemy.ctipresences import CtiPresences
from xivo_dao.alchemy.dialaction import Dialaction
from xivo_dao.alchemy.features import Features
from xivo_dao.alchemy.linefeatures import LineFeatures
from xivo_dao.alchemy.phonefunckey import PhoneFunckey
from xivo_dao.alchemy.queuemember import QueueMember
from xivo_dao.alchemy.rightcallmember import RightCallMember
from xivo_dao.alchemy.schedulepath import SchedulePath
from xivo_dao.alchemy.userfeatures import UserFeatures
from xivo_dao.tests import test_dao
from xivo_test_helpers.asset_launching_test_case import AssetLaunchingTestCase

DB_USER = 'asterisk'
DB_PASSWORD = 'proformatique'
DB_HOST = 'localhost'
DB_PORT = '15432'
DB_NAME = 'asterisk'
DB_URL = ('postgresql://{user}:{password}@{host}:{port}/{db_name}'
          .format(user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT, db_name=DB_NAME))

test_dao.TEST_DB_URL = DB_URL


class _IntegrationUser(AssetLaunchingTestCase):

    assets_root = os.path.join(os.path.dirname(__file__), '..', 'assets')
    asset = 'database'
    service = 'ctid'


class TestDatabaseDAO(test_dao.DAOTestCase):

    @classmethod
    def setUpClass(cls):
        _IntegrationUser.setUpClass()
        super(TestDatabaseDAO, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        super(TestDatabaseDAO, cls).tearDownClass()
        _IntegrationUser.tearDownClass()

    def test_get_transfer_dial_timeout(self):
        feature = Features()
        feature.filename = 'features.conf'
        feature.category = 'general'
        feature.var_name = 'atxfernoanswertimeout'
        feature.var_val = '5'
        self.add_me(feature)

        result = transfer_dao.get_transfer_dial_timeout()

        assert_that(result, equal_to(5))

    def test_enable_recording(self):
        user_id = self.add_user_recording_disabled()

        user_dao.enable_service(user_id, 'callrecord')

        self._check_recording(user_id, 1)

    def test_disable_recording(self):
        user_id = self.add_user_recording_enabled()

        user_dao.disable_service(user_id, 'callrecord')

        self._check_recording(user_id, 0)

    def _check_recording(self, user_id, value):
        user_features = (self.session.query(UserFeatures)
                         .filter(UserFeatures.id == user_id))[0]
        self.assertEquals(user_features.callrecord, value)

    def add_user_recording_disabled(self):
        user = self.add_user(firstname='firstname_recording not set', callrecord=0)
        return user.id

    def add_user_recording_enabled(self):
        user = self.add_user(firstname='firstname_recording set', callrecord=1)
        return user.id

    def test_enable_unconditional_fwd(self):
        destination = '765'
        user_id = self.add_user_with_unconditional_fwd(destination, 0)

        user_dao.enable_service(user_id, 'enableunc', 'destunc', destination)

        self._check_unconditional_fwd_in_db(user_id, 1)
        self._check_unconditional_dest_in_db(user_id, destination)

    def add_user_with_unconditional_fwd(self, destination, enabled):
        user = self.add_user(firstname='firstname_unconditional_fwd',
                             enableunc=enabled,
                             destunc=destination)
        return user.id

    def _check_unconditional_fwd_in_db(self, user_id, value):
        user_features = (self.session.query(UserFeatures)
                         .filter(UserFeatures.id == user_id))[0]
        self.assertEquals(user_features.enableunc, value)

    def test_unconditional_fwd_disabled(self):
        destination = '4321'
        user_id = self.add_user_with_unconditional_fwd('', 0)

        user_dao.disable_service(user_id, 'enableunc', 'destunc', destination)

        self._check_unconditional_fwd_in_db(user_id, 0)
        self._check_unconditional_dest_in_db(user_id, destination)

    def _check_unconditional_dest_in_db(self, user_id, destination):
        user_features = (self.session.query(UserFeatures)
                         .filter(UserFeatures.id == user_id))[0]
        self.assertEquals(user_features.destunc, destination)

    def test_rna_fwd_enabled(self):
        destination = '4321'
        user_id = self.add_user_with_rna_fwd('', 1)

        user_dao.enable_service(user_id, 'enablerna', 'destrna', destination)

        self._check_rna_fwd_in_db(user_id, 1)
        self._check_rna_dest_in_db(user_id, destination)

    def test_rna_fwd_disabled(self):
        destination = '4325'
        user_id = self.add_user_with_rna_fwd('', 0)

        user_dao.disable_service(user_id, 'enablerna', 'destrna', destination)

        self._check_rna_fwd_in_db(user_id, 0)
        self._check_rna_dest_in_db(user_id, destination)

    def add_user_with_rna_fwd(self, destination, enabled):
        user = self.add_user(firstname='firstname_rna_fwd',
                             enablerna=enabled,
                             destrna=destination)
        return user.id

    def _check_rna_dest_in_db(self, user_id, destination):
        user_features = (self.session.query(UserFeatures)
                         .filter(UserFeatures.id == user_id))[0]
        self.assertEquals(user_features.destrna, destination)

    def _check_rna_fwd_in_db(self, user_id, value):
        user_features = (self.session.query(UserFeatures)
                         .filter(UserFeatures.id == user_id))[0]
        self.assertEquals(user_features.enablerna, value)

    def add_user_with_busy_fwd(self, destination, enabled):
        user = self.add_user(firstname='firstname_busy_fwd', enablebusy=enabled, destbusy=destination)
        return user.id

    def _check_busy_fwd_in_db(self, user_id, value):
        user_features = (self.session.query(UserFeatures)
                         .filter(UserFeatures.id == user_id))[0]
        self.assertEquals(user_features.enablebusy, value)

    def _check_busy_dest_in_db(self, user_id, destination):
        user_features = (self.session.query(UserFeatures)
                         .filter(UserFeatures.id == user_id))[0]
        self.assertEquals(user_features.destbusy, destination, 'Destination not updated')

    def test_busy_fwd_disabled(self):
        destination = '435'
        user_id = self.add_user_with_busy_fwd('456', 1)

        user_dao.disable_service(user_id, 'enablebusy', 'destbusy', destination)

        self._check_busy_fwd_in_db(user_id, 0)
        self._check_busy_dest_in_db(user_id, destination)

    def test_busy_fwd_enabled(self):
        destination = '435'
        user_id = self.add_user_with_busy_fwd('456', 0)

        user_dao.enable_service(user_id, 'enablebusy', 'destbusy', destination)

        self._check_busy_fwd_in_db(user_id, 1)
        self._check_busy_dest_in_db(user_id, destination)

    def _add_presence(self, name):
        cti_presence = CtiPresences()
        cti_presence.name = name

        self.add_me(cti_presence)

        return cti_presence.id

    def _add_phone_hints_group(self, name):
        cti_phone_hints_group = CtiPhoneHintsGroup()
        cti_phone_hints_group.name = name

        self.add_me(cti_phone_hints_group)

        return cti_phone_hints_group.id

    def _add_profile(self, name):
        cti_profile = CtiProfile()
        cti_profile.name = name
        cti_profile.presence_id = self._add_presence('test_presence')
        cti_profile.phonehints_id = self._add_phone_hints_group('test_add_phone_hints_group')

        self.add_me(cti_profile)

        return cti_profile.id

    def add_user_to_queue(self, userid, queuename):
        queuemember = QueueMember(usertype='user',
                                  userid=userid,
                                  category='queue',
                                  queue_name=queuename,
                                  interface='SIP/stuff',
                                  channel='SIP')
        self.add_me(queuemember)

    def add_user_to_rightcall(self, userid, rightcallid):
        member = RightCallMember(type='user', typeval=str(userid), rightcallid=rightcallid)
        self.add_me(member)

    def add_user_to_boss_secretary_callfilter(self, userid, callfilter_name):
        callfilter = Callfilter(type='bosssecretary',
                                name=callfilter_name,
                                bosssecretary='secretary-simult',
                                callfrom='all',
                                description='')
        self.add_me(callfilter)
        member = Callfiltermember(type='user',
                                  typeval=str(userid),
                                  callfilterid=callfilter.id,
                                  bstype='boss')
        self.add_me(member)

    def _add_dialaction_to_user(self, userid):
        dialaction = Dialaction(event='answer', category='user', categoryval=str(userid), action='none')
        self.add_me(dialaction)

    def _add_function_key_to_user(self, userid):
        key = PhoneFunckey(iduserfeatures=userid, fknum=1, typeextenumbersright='user')
        self.add_me(key)

    def _add_schedule_to_user(self, userid, scheduleid):
        path = SchedulePath(schedule_id=scheduleid, path='user', pathid=userid, order=0)
        self.add_me(path)

    def test_get_reachable_contexts(self):
        context = 'my_context'

        user_line = self.add_user_line_with_exten(context=context)

        result = user_dao.get_reachable_contexts(user_line.user.id)

        self.assertEqual(result, [context])

    def test_get_reachable_context_no_line(self):
        user = self.add_user(firstname='Tester')

        self.assertEqual(user_dao.get_reachable_contexts(user.id), [])

    def test_get_reachable_context_included_ctx(self):
        context = 'my_context'
        included_context = 'second_ctx'

        ctx_include = ContextInclude()
        ctx_include.context = context
        ctx_include.include = included_context

        self.add_me(ctx_include)

        user_line = self.add_user_line_with_exten(context=context)

        result = user_dao.get_reachable_contexts(user_line.user.id)

        assert_that(result, contains_inanyorder(context, included_context))

    def test_get_reachable_context_loop(self):
        context = 'my_context'
        included_context = 'second_ctx'
        looping_context = 'third_ctx'

        ctx = ContextInclude()
        ctx.context = context
        ctx.include = included_context

        ctx_include = ContextInclude()
        ctx_include.context = included_context
        ctx_include.include = looping_context

        ctx_loop = ContextInclude()
        ctx_loop.context = looping_context
        ctx_loop.include = context

        map(self.add_me, [ctx, ctx_include, ctx_loop])

        user_line = self.add_user_line_with_exten(context=context)

        result = user_dao.get_reachable_contexts(user_line.user.id)

        for context in [context, included_context, looping_context]:
            self.assertTrue(context in result)

    def test_get_name_number(self):
        firstname = 'Toto'
        lastname = 'Plop'
        exten = '1234'
        user_line = self.add_user_line_with_exten(exten=exten,
                                                  firstname=firstname,
                                                  lastname=lastname)
        expected_name = '{user.firstname} {user.lastname}'.format(user=user_line.user)

        name, number = user_dao.get_name_number(user_line.user.id)

        self.assertEqual(name, expected_name)
        self.assertEqual(number, exten)

    def test_get_device_id_with_one_user(self):
        device_id = 'qwertyuiopasdfghjklzxcvbnm'
        user_line = self.add_user_line_with_exten(device=device_id)

        result = user_dao.get_device_id(user_line.user.id)

        self.assertEqual(result, device_id)

    def test_get_device_id_no_device_one_line(self):
        user = self.add_user(firstname='Toto', lastname='Plop')

        line = LineFeatures()
        line.number = '1234'
        line.name = '12kjdhf'
        line.context = 'context'
        line.provisioningid = 1234
        line.protocol = 'sip'
        line.protocolid = 1
        line.device = ''

        self.add_me(line)

        self.assertRaises(LookupError, user_dao.get_device_id, user.id)

    def test_get_device_id_with_two_users(self):
        device_id = 'qwertyuiopasdfghjklzxcvbnm'
        self.add_user_line_with_exten(exten='1002',
                                      device=device_id)
        user_line_2 = self.add_user_line_with_exten(device=device_id)

        result = user_dao.get_device_id(user_line_2.user.id)

        self.assertEqual(result, device_id)

    def test_get_device_id_no_line(self):
        user = self.add_user(firstname='Toto', lastname='Plop')

        self.assertRaises(LookupError, user_dao.get_device_id, user.id)

    def test_get_device_id_no_user(self):
        self.assertRaises(LookupError, user_dao.get_device_id, 666)

    def test_find_line_context(self):
        user_line = self.add_user_line_with_exten()
        expected_context = user_line.line.context

        context = user_dao.find_line_context(user_line.user.id)

        self.assertEquals(context, expected_context)

    def test_find_line_context_no_line(self):
        user = self.add_user(firstname='test_user1')

        context = user_dao.find_line_context(user.id)

        self.assertEqual(context, None)

    def _assert_no_queue_member_for_user(self, user_id):
        queue_member_for_user = (self.session.query(QueueMember)
                                             .filter(QueueMember.usertype == 'user')
                                             .filter(QueueMember.userid == user_id)
                                             .first())
        self.assertEquals(None, queue_member_for_user)

    def _assert_no_rightcall_for_user(self, user_id):
        rightcallmember_for_user = (self.session.query(RightCallMember)
                                                .filter(RightCallMember.type == 'user')
                                                .filter(RightCallMember.typeval == str(user_id))
                                                .first())
        self.assertEquals(None, rightcallmember_for_user)

    def _assert_no_callfilter_for_user(self, user_id):
        callfiltermember_for_user = (self.session.query(Callfiltermember)
                                                 .filter(Callfiltermember.type == 'user')
                                                 .filter(Callfiltermember.typeval == str(user_id))
                                                 .first())
        self.assertEquals(None, callfiltermember_for_user)

    def _assert_no_dialaction_for_user(self, user_id):
        user_dialaction = (self.session.query(Dialaction)
                                       .filter(Dialaction.category == 'user')
                                       .filter(Dialaction.categoryval == str(user_id))
                                       .first())
        self.assertEquals(None, user_dialaction)

    def _assert_no_funckey_for_user(self, user_id):
        user_key = (self.session.query(PhoneFunckey)
                                .filter(PhoneFunckey.iduserfeatures == user_id)
                                .first())
        self.assertEquals(None, user_key)

    def _assert_no_schedule_for_user(self, user_id):
        schedulepath = (self.session.query(SchedulePath).filter(SchedulePath.path == 'user')
                                    .filter(SchedulePath.pathid == user_id)
                                    .first())
        self.assertEquals(None, schedulepath)

    def test_that_get_user_config_contains_the_xivo_uuid(self):
        infos = self.add_infos()
        uuid = infos.uuid
        user_line = self.add_user_line_with_exten()
        user_id = user_line.user.id

        user_config = user_dao.get_user_config(user_line.user.id)

        assert_that(user_config[str(user_id)]['xivo_uuid'], equal_to(uuid))

    def test_get_user_config(self):
        infos = self.add_infos()
        firstname = u'Jack'
        lastname = u'Strap'
        fullname = u'%s %s' % (firstname, lastname)
        callerid = u'"%s"' % fullname
        context = u'mycontext'

        user_line = self.add_user_line_with_exten(firstname=firstname,
                                                  lastname=lastname,
                                                  context=context,
                                                  exten='1234',
                                                  name='12kjdhf',
                                                  provisioningid=1234,
                                                  protocolid=1,
                                                  musiconhold=u'')

        user_id = user_line.user.id
        line_list = (str(user_line.line.id),)
        expected = {
            str(user_id): {
                'agentid': None,
                'bsfilter': 'no',
                'callerid': callerid,
                'callrecord': 0,
                'commented': 0,
                'context': context,
                'cti_profile_id': None,
                'description': None,
                'destbusy': u'',
                'destrna': u'',
                'destunc': u'',
                'enableonlinerec': 0,
                'enablebusy': 0,
                'enableclient': 0,
                'enablednd': 0,
                'enablehint': 1,
                'enablerna': 0,
                'enableunc': 0,
                'enablevoicemail': 0,
                'entityid': None,
                'firstname': firstname,
                'fullname': fullname,
                'id': user_id,
                'uuid': user_line.user.uuid,
                'identity': fullname,
                'incallfilter': 0,
                'language': None,
                'lastname': lastname,
                'linelist': line_list,
                'loginclient': u'',
                'mobilephonenumber': u'',
                'musiconhold': u'',
                'outcallerid': u'',
                'passwdclient': u'',
                'pictureid': None,
                'preprocess_subroutine': None,
                'rightcallcode': None,
                'ringextern': None,
                'ringforward': None,
                'ringgroup': None,
                'ringintern': None,
                'ringseconds': 30,
                'simultcalls': 5,
                'timezone': None,
                'userfield': None,
                'voicemailid': None,
                'xivo_uuid': infos.uuid,
            }
        }

        result = user_dao.get_user_config(user_id)

        result_dict = result[str(user_id)]
        expected_dict = expected[str(user_id)]

        for key, expected_value in expected_dict.iteritems():
            result_value = result_dict[key]
            assert_that(expected_value, equal_to(result_value),
                        'key %r does not match' % key)
        assert_that(result, equal_to(expected))

    def test_get_user_config_with_no_line(self):
        self.add_infos()
        user = self.add_user()
        user_id = user.id

        result = user_dao.get_user_config(user_id)

        assert_that(result[str(user_id)]['context'], none())
        assert_that(result[str(user_id)]['linelist'], empty())

    def test_get_user_config_no_user(self):
        self.add_infos()
        self.assertRaises(LookupError, user_dao.get_user_config, 8921890)

    def test_get_users_config(self):
        self.add_infos()
        user1 = self.add_user(
            firstname='John',
            lastname='Jackson',
        )
        user2 = self.add_user(
            firstname='Jack',
            lastname='Johnson',
        )
        user1_id = str(user1.id)
        user2_id = str(user2.id)

        user1_firstname = user1.firstname
        user2_firstname = user2.firstname

        result = user_dao.get_users_config()

        assert_that(result, contains_inanyorder(user1_id, user2_id))
        assert_that(result[user1_id]['firstname'], equal_to(user1_firstname))
        assert_that(result[user2_id]['firstname'], equal_to(user2_firstname))
