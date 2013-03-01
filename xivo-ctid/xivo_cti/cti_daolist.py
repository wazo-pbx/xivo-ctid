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
from xivo_dao import line_dao, group_dao, agent_dao, \
    meetme_dao, queue_dao, voicemail_dao, context_dao, \
    phonebook_dao, user_dao, trunk_dao

logger = logging.getLogger('daolist')


class UnknownListName(Exception):
    pass


class DaoList(object):

    def __init__(self, listname):
        self.listname = listname

    def get(self, id):
            name = '_get_%s' % self.listname[0:-1]
            return self._get(name, id)

    def get_list(self):
            name = '_get_%s' % self.listname
            return self._get(name)

    def _get(self, name, id=None):
        try:
            if id:
                return getattr(self, name)(id)
            else:
                return getattr(self, name)()
        except LookupError:
            return {}
        except AttributeError:
            raise UnknownListName()

    def _get_users(self):
        res = {}
        users = user_dao.all_join_line_id()
        for row in users:
            user, line_id = row
            res.update(self._format_user_data(user, line_id))
        return res

    def _get_user(self, id):
        user, line_id = user_dao.get_join_line_id_with_user_id(id)
        return self._format_user_data(user, line_id)

    def _format_user_data(self, user, line_id):
        res = {}
        key = str(user.id)
        res[key] = user.__dict__
        res[key]['fullname'] = '%s %s' % (user.firstname, user.lastname)
        res[key]['identity'] = res[str(user.id)]['fullname']
        res[key]['linelist'] = [str(line_id)]
        return res

    def _get_phones(self):
        full_line = []
        full_line.extend(line_dao.all_with_protocol('sip'))
        full_line.extend(line_dao.all_with_protocol('iax'))
        full_line.extend(line_dao.all_with_protocol('sccp'))
        full_line.extend(line_dao.all_with_protocol('custom'))

        res = {}
        for line in full_line:
            line, protocol, firstname, lastname = line
            res.update(self._format_line_data(line, protocol, firstname, lastname))
        return res

    def _get_phone(self, id):
        line, protocol, firstname, lastname = line_dao.get_with_line_id(id)
        return self._format_line_data(line, protocol, firstname, lastname)

    def _format_line_data(self, line, protocol, firstname, lastname):
        res = {}
        merged_line = protocol.__dict__
        merged_line.update(line.__dict__)
        merged_line['useridentity'] = '%s %s' % (firstname, lastname)
        protocol = merged_line['protocol'].upper()
        iface_name = merged_line['name']
        merged_line['identity'] = '%s/%s' % (protocol, iface_name)
        res[str(line.id)] = merged_line
        return res

    def _get_groups(self):
        res = {}
        groups = group_dao.all()
        for group in groups:
            res.update(self._format_group_data(group))
        return res

    def _get_group(self, id):
        group = group_dao.get(id)
        return self._format_group_data(group)

    def _format_group_data(self, group):
        res = {}
        key = str(group.id)
        res[key] = group.__dict__
        res[key]['fullname'] = '%s (%s)' % (group.name, group.context)
        return res

    def _get_agents(self):
        res = {}
        agents = agent_dao.all()
        for agent in agents:
            res.update(self._format_agent_data(agent))
        return res

    def _get_agent(self, id):
        agent = agent_dao.get(id)
        return self._format_agent_data(agent)

    def _format_agent_data(self, agent):
        res = {}
        key = str(agent.id)
        res[key] = agent.__dict__
        return res

    def _get_meetmes(self):
        res = {}
        meetmes = meetme_dao.all()
        for meetme in meetmes:
            res.update(self._format_meetme_data(meetme))
        return res

    def _get_meetme(self, id):
        meetme = meetme_dao.get(id)
        return self._format_meetme_data(meetme)

    def _format_meetme_data(self, meetme):
        res = {}
        key = str(meetme.id)
        res[key] = meetme.__dict__
        return res

    def _get_queues(self):
        res = {}
        queues = queue_dao.all_queues()
        for queue in queues:
            res.update(self._format_queue_data(queue))
        return res

    def _get_queue(self, id):
        queue = queue_dao.get(id)
        return self._format_queue_data(queue)

    def _format_queue_data(self, queue):
        res = {}
        key = str(queue.id)
        res[key] = queue.__dict__
        res[key]['identity'] = '%s (%s@%s)' % (queue.displayname, queue.number, queue.context)
        return res

    def _get_voicemails(self):
        res = {}
        voicemails = voicemail_dao.all()
        for voicemail in voicemails:
            res.update(self._format_voicemail_data(voicemail))
        return res

    def _get_voicemail(self, id):
        voicemail = voicemail_dao.get(id)
        return self._format_voicemail_data(voicemail)

    def _format_voicemail_data(self, voicemail):
        res = {}
        key = str(voicemail.uniqueid)
        res[key] = voicemail.__dict__
        res[key]['fullmailbox'] = '%s@%s' % (voicemail.mailbox, voicemail.context)
        res[key]['identity'] = '%s (%s@%s)' % (voicemail.fullname, voicemail.mailbox, voicemail.context)
        return res

    def _get_contexts(self):
        res = {}
        contexts = context_dao.all()
        for row in contexts:
            context, contextnumbers, contexttype, contextinclude = row
            res.update(self._format_context_data(context, contextnumbers, contexttype, contextinclude))
        return res

    def _get_context(self, id):
        context, contextnumbers, contexttype, contextinclude = context_dao.get_join_elements(id)
        return self._format_context_data(context, contextnumbers, contexttype, contextinclude)

    def _format_context_data(self, context, contextnumbers, contexttype, contextinclude):
        res = {}
        key = str(context.name)
        res[key]['context'] = context.todict()
        res[key]['contextnumbers'] = contextnumbers.todict()
        res[key]['contextinclude'] = contextinclude.todict() if contextinclude else False
        res[key]['contexttype'] = contexttype.todict()
        return res

    def _get_phonebooks(self):
        res = {}
        phonebooks = phonebook_dao.all_join_elements()
        for row in phonebooks:
            phonebook, phonebookaddress, phonebooknumber = row
            res.update(self._format_phonebook_data(phonebook, phonebookaddress, phonebooknumber))
        return res

    def _get_phonebook(self, id):
        phonebook = phonebook_dao.get(id)
        phonebookaddress = phonebook_dao.get_phonebookaddress(id)
        phonebooknumber = phonebook_dao.get_phonebooknumber(id)
        return self._format_phonebook_data(phonebook, phonebookaddress, phonebooknumber)

    def _format_phonebookaddress(self, phonebookaddress):
        phonebookaddress_dict = {}
        for pba in phonebookaddress:
            phonebookaddress_dict[pba.type] = pba.todict()
        return phonebookaddress_dict

    def _format_phonebooknumber(self, phonebooknumber):
        phonebooknumber_dict = {}
        for pbn in phonebooknumber:
            phonebooknumber_dict[pbn.type] = pbn.todict()
        return phonebooknumber_dict

    def _format_phonebook_data(self, phonebook, phonebookaddress, phonebooknumber):
        res = {}
        key = str(phonebook.id)
        res[key] = {}
        res[key]['phonebook'] = phonebook.todict()
        res[key]['phonebookaddress'] = self._format_phonebookaddress(phonebookaddress)
        res[key]['phonebooknumber'] = self._format_phonebooknumber(phonebooknumber) if phonebooknumber else False
        return res

    def _get_trunks(self):
        res = {}
        trunks = trunk_dao.all()
        for trunk in trunks:
            res.update(self._format_trunk_data(trunk))
        return res

    def _get_trunk(self, id):
        trunk = trunk_dao.get(id)
        return self._format_trunk_data(trunk)

    def _format_trunk_data(self, trunk):
        res = {}
        key = str(trunk.id)
        res[key] = trunk.__dict__
        return res
