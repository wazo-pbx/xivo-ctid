# -*- coding: utf-8 -*-

# XiVO CTI Server
#
# Copyright (C) 2012  Avencall
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

import logging
from xivo_cti.dao import userfeaturesdao
from xivo_dao import linefeaturesdao, group_dao, agentfeaturesdao, \
    meetme_features_dao, queue_features_dao, voicemail_dao, context_dao, \
    phonebook_dao, incall_dao
from pprint import pprint

logger = logging.getLogger('daolist')


class DaoList(object):

    def __init__(self, listname):
        self.listname = listname

    def get_list(self):
        if self.listname == 'users':
            return self._get_users()
        elif self.listname == 'lines':
            return self._get_lines()
        elif self.listname == 'groups':
            return self._get_groups()
        elif self.listname == 'agents':
            return self._get_agents()
        elif self.listname == 'meetme':
            return self._get_meetmes()
        elif self.listname == 'meetme':
            return self._get_meetmes()
        elif self.listname == 'queues':
            return self._get_queues()
        elif self.listname == 'voicemail':
            return self._get_voicemails()
        elif self.listname == 'context':
            return self._get_contexts()
        elif self.listname == 'phonebook':
            return self._get_phonebooks()
        elif self.listname == 'incall':
            return self._get_incalls()

        return {}

    def _get_users(self):
        res = {}
        users = userfeaturesdao.all()
        for user in users:
            key = str(user.id)
            res[key] = user.todict()
            res[key]['fullname'] = '%s %s' % (user.firstname, user.lastname)
            res[key]['identity'] = res[str(user.id)]['fullname']
        return res

    def _get_groups(self):
        res = {}
        groups = group_dao.all()
        for group in groups:
            key = str(group.id)
            res[key] = group.todict()
            res[key]['fullname'] = '%s (%s)' % (group.name, group.context)
        return res

    def _get_queues(self):
        res = {}
        queues = queue_features_dao.all()
        for queue in queues:
            key = str(queue.id)
            res[key] = queue.todict()
            res[key]['identity'] = '%s (%s@%s)' % (queue.displayname, queue.number, queue.context)
        return res

    def _get_agents(self):
        res = {}
        agents = agentfeaturesdao.all()
        for agent in agents:
            res[str(agent.id)] = agent.todict()
        return res

    def _get_meetmes(self):
        res = {}
        meetmes = meetme_features_dao.all()
        for meetme in meetmes:
            res[str(meetme.id)] = meetme.todict()
        return res

    def _get_voicemails(self):
        res = {}
        voicemails = voicemail_dao.all()
        for voicemail in voicemails:
            key = str(voicemail.uniqueid)
            res[key] = voicemail.todict()
            res[key]['fullmailbox'] = '%s@%s' % (voicemail.mailbox, voicemail.context)
            res[key]['identity'] = '%s (%s@%s)' % (voicemail.fullname, voicemail.mailbox, voicemail.context)
        return res

    def _get_lines(self):
        full_line = []
        full_line.extend(linefeaturesdao.all_with_protocol('sip'))
        full_line.extend(linefeaturesdao.all_with_protocol('iax'))
        full_line.extend(linefeaturesdao.all_with_protocol('sccp'))
        full_line.extend(linefeaturesdao.all_with_protocol('custom'))

        res = {}
        for line in full_line:
            linefeatures, protocol = line
            merged_line = protocol.__dict__
            merged_line.update(linefeatures.todict())
            res[str(linefeatures.id)] = merged_line
        return res

    def _get_contexts(self):
        res = {}
        contexts = context_dao.all()
        for row in contexts:
            context, contextnumbers, contextinclude, contexttype = row
            key = str(context.name)
            res[key]['context'] = context.todict()
            res[key]['contextnumbers'] = contextnumbers.todict()
            res[key]['contextinclude'] = contextinclude.todict() if contextinclude else False
            res[key]['contexttype'] = contexttype.todict()
        return res

    def _get_phonebooks(self):
        res = {}
        phonebooks = phonebook_dao.all()
        for row in phonebooks:
            phonebook, phonebookaddress, phonebooknumber = row
            key = str(phonebook.id)
            res[key] = {}
            res[key]['phonebook'] = phonebook.todict()
            res[key]['phonebookaddress'] = phonebookaddress.todict()
            res[key]['phonebooknumber'] = phonebooknumber.todict() if phonebooknumber else False
        return res

    def _get_incalls(self):
        res = {}
        incalls = incall_dao.all()
        for row in incalls:
            pprint(row)
            incall, dialaction, user, group, queue, meetme, voicemail, voicemenu = row
        return res
