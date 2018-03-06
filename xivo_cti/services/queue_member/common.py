# -*- coding: utf-8 -*-
# Copyright (C) 2007-2014 Avencall
# SPDX-License-Identifier: GPL-3.0+


def format_member_name_of_agent(agent_number):
    return 'Agent/%s' % agent_number


def format_queue_member_id(queue_name, member_name):
    return '%s,%s' % (member_name, queue_name)


def is_agent_member_name(member_name):
    return member_name.startswith('Agent/')
