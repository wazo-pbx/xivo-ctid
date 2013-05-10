# -*- coding: utf-8 -*-

# XiVO CTI Server

# Copyright (C) 2007-2012  Avencall'
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Alternatively, XiVO CTI Server is available under other licenses directly
# contracted with Avencall. See the LICENSE file at top of the souce tree
# or delivered in the installable package in which XiVO CTI Server is
# distributed for more details.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import unittest
from xivo_cti.cti_daolist import DaoList, UnknownListName
from mock import Mock, patch, sentinel


class TestDaoList(unittest.TestCase):

    def setUp(self):
        self.daolist = DaoList('')

    def test_get_with_user(self):
        user_id = 1
        expected_result = {
            1: {
                'firtname': 'henri',
                'lstname': 'bob'
            }
        }
        self.daolist.listname = 'users'
        self.daolist._get_user = Mock()
        self.daolist._get_user.return_value = expected_result

        result = self.daolist.get(user_id)

        self.daolist._get_user.assert_called_once_with(user_id)
        self.assertEquals(result, expected_result)

    @patch('xivo_dao.user_dao.get_users_config')
    def test_get_users(self, mock_get_users_config):
        mock_get_users_config.return_value = sentinel.value

        result = self.daolist._get_users()

        mock_get_users_config.assert_called_once_with()
        self.assertEqual(result, sentinel.value)

    @patch('xivo_dao.user_dao.get_user_config')
    def test_get_user(self, mock_get_user_config):
        mock_get_user_config.return_value = sentinel.value

        result = self.daolist._get_user(sentinel.user_id)

        mock_get_user_config.assert_called_once_with(sentinel.user_id)
        self.assertEqual(result, sentinel.value)

    def test_get_with_agents(self):
        agent_id = 1
        expected_result = {
            1: {
                'firtname': 'henri',
                'lstname': 'bob'
            }
        }
        self.daolist.listname = 'agents'
        self.daolist._get_agent = Mock()
        self.daolist._get_agent.return_value = expected_result

        result = self.daolist.get(agent_id)

        self.daolist._get_agent.assert_called_once_with(agent_id)
        self.assertEquals(result, expected_result)

    def test_get_with_unknown_listname(self):
        self.daolist.listname = 'unknown'

        self.assertRaises(UnknownListName, self.daolist.get, 1)

    def test_get_with_no_result(self):
        user_id = 1
        self.daolist.listname = 'users'
        self.daolist._get_user = Mock()
        self.daolist._get_user.side_effect = LookupError

        result = self.daolist.get(user_id)

        self.assertEquals(result, {})

    def _generic_object(self, **variables):
        class generic(object):
            def __init__(self):
                for key, var in variables.iteritems():
                    setattr(self, key, var)

            def todict(self):
                return dict(self.__dict__)

        return generic()

    def test_format_line_data(self):
        line_id = 7
        protocol_id = 12
        user_id = 76
        protocol_name = 'iuds98f'
        firstname, lastname = 'Lord', 'Sanderson'
        proto = 'sip'
        linefeatures = self._generic_object(id=line_id,
                                            protocolid=protocol_id,
                                            iduserfeatures=user_id)
        protocol = self._generic_object(id=protocol_id,
                                        name=protocol_name,
                                        protocol=proto)

        expected_result = {
            str(line_id): {
                'id': line_id,
                'protocolid': protocol_id,
                'iduserfeatures': user_id,
                'name': protocol_name,
                'protocol': proto,
                'useridentity': '%s %s' % (firstname, lastname),
                'identity': '%s/%s' % (proto.upper(), protocol_name)
            }
        }

        result = self.daolist._format_line_data(linefeatures, protocol, firstname, lastname)

        self.assertEquals(result, expected_result)

    def test_format_group_data(self):
        group_id = 7
        name = 'test_group'
        context = 'default'
        number = '2000'
        group = self._generic_object(id=group_id,
                                     name=name,
                                     context=context,
                                     number=number)

        expected_result = {
            str(group_id): {
                'id': group_id,
                'name': name,
                'context': context,
                'number': number,
                'fullname': '%s (%s)' % (group.name, group.context)
            }
        }

        result = self.daolist._format_group_data(group)

        self.assertEquals(result, expected_result)

    def test_format_agent_data(self):
        agent_id = 3
        name = 'test_agent'
        context = 'default'
        number = '2000'
        agent = self._generic_object(id=agent_id,
                                     name=name,
                                     context=context,
                                     number=number)

        expected_result = {
            str(agent_id): {
                'id': agent_id,
                'name': name,
                'context': context,
                'number': number
            }
        }

        result = self.daolist._format_agent_data(agent)

        self.assertEquals(result, expected_result)

    def test_format_meetme_data(self):
        meetme_id = 3
        name = 'test_meetme'
        context = 'default'
        confno = '2000'
        meetme = self._generic_object(
            id=meetme_id,
            name=name,
            context=context,
            confno=confno
        )

        expected_result = {
            str(meetme_id): {
                'id': meetme_id,
                'name': name,
                'context': context,
                'confno': confno
            }
        }

        result = self.daolist._format_meetme_data(meetme)

        self.assertEquals(result, expected_result)

    def test_format_queue_data(self):
        queue_id = 7
        name = 'test_queue'
        displayname = 'test queue'
        context = 'default'
        number = '2000'
        queue = self._generic_object(id=queue_id,
                                     name=name,
                                     displayname=displayname,
                                     context=context,
                                     number=number)

        expected_result = {
            str(queue_id): {
                'id': queue_id,
                'name': name,
                'displayname': displayname,
                'context': context,
                'number': number,
                'identity': '%s (%s@%s)' % (displayname, number, context)
            }
        }

        result = self.daolist._format_queue_data(queue)

        self.assertEquals(result, expected_result)

    def test_format_voicemail_data(self):
        voicemail_id = 42
        mailbox = 'test_queue'
        fullname = 'test queue'
        context = 'default'
        number = '2000'
        voicemail = self._generic_object(uniqueid=voicemail_id,
                                     mailbox=mailbox,
                                     fullname=fullname,
                                     context=context,
                                     number=number)

        expected_result = {
            str(voicemail_id): {
                'uniqueid': voicemail_id,
                'mailbox': mailbox,
                'fullname': fullname,
                'context': context,
                'number': number,
                'fullmailbox': '%s@%s' % (mailbox, context),
                'identity': '%s (%s@%s)' % (fullname, mailbox, context)
            }
        }

        result = self.daolist._format_voicemail_data(voicemail)

        self.assertEquals(result, expected_result)

    def test_format_trunk_data(self):
        trunk_id = 42
        protocol = 'sip'
        protocolid = 15
        registerid = 0
        trunk = self._generic_object(id=trunk_id,
                                     protocol=protocol,
                                     protocolid=protocolid,
                                     registerid=registerid)

        expected_result = {
            str(trunk_id): {
                'id': trunk_id,
                'protocol': protocol,
                'protocolid': protocolid,
                'registerid': registerid
            }
        }

        result = self.daolist._format_trunk_data(trunk)

        self.assertEquals(result, expected_result)
