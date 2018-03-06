# -*- coding: utf-8 -*-
# Copyright (C) 2015-2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.alchemy.contextinclude import ContextInclude
from xivo_dao.alchemy.extension import Extension
from xivo_dao.alchemy.infos import Infos
from xivo_dao.alchemy.linefeatures import LineFeatures as Line
from xivo_dao.alchemy.user_line import UserLine
from xivo_dao.alchemy.line_extension import LineExtension
from xivo_dao.alchemy.userfeatures import UserFeatures as User
from xivo_dao.helpers.db_utils import session_scope

USER_CONFIG_FIELDS = (
    'agentid',
    'bsfilter',
    'callerid',
    'callrecord',
    'commented',
    'cti_profile_id',
    'description',
    'destbusy',
    'destrna',
    'destunc',
    'enableonlinerec',
    'enablebusy',
    'enableclient',
    'enablednd',
    'enablehint',
    'enablerna',
    'enableunc',
    'enablevoicemail',
    'entityid',
    'firstname',
    'fullname',
    'id',
    'uuid',
    'incallfilter',
    'language',
    'lastname',
    'loginclient',
    'mobilephonenumber',
    'musiconhold',
    'outcallerid',
    'passwdclient',
    'pictureid',
    'preprocess_subroutine',
    'rightcallcode',
    'ringextern',
    'ringforward',
    'ringgroup',
    'ringintern',
    'ringseconds',
    'simultcalls',
    'timezone',
    'userfield',
    'voicemailid',
)


def enable_service(user_id, enable_name, dest_name=None, dest_value=None):
    data = {enable_name: 1}
    if dest_name and dest_value:
        data[dest_name] = dest_value

    with session_scope() as session:
        session.query(User).filter_by(id=user_id).update(data)


def disable_service(user_id, enable_name, dest_name=None, dest_value=None):
    data = {enable_name: 0}
    if dest_name and dest_value:
        data[dest_name] = dest_value

    with session_scope() as session:
        session.query(User).filter_by(id=user_id).update(data)


def find_line_context(user_id):
    with session_scope() as session:
        query = (session.query(Line.context)
                 .join(UserLine.main_line_rel)
                 .join(UserLine.main_user_rel)
                 .filter(UserLine.user_id == user_id))
        return query.scalar()


def get_reachable_contexts(user_id):
    with session_scope() as session:
        query = (session.query(Extension.context)
                 .join(LineExtension.main_extension_rel)
                 .join(UserLine.main_user_rel)
                 .filter(UserLine.user_id == user_id))
        contexts = [row.context for row in query]
        return _get_nested_contexts(session, contexts)


def _get_nested_contexts(session, contexts):
    checked = []
    to_check = set(contexts) - set(checked)
    while to_check:
        context = to_check.pop()
        contexts.extend(_get_included_contexts(session, context))
        checked.append(context)
        to_check = set(contexts) - set(checked)

    return list(set(contexts))


def _get_included_contexts(session, context):
    query = (session.query(ContextInclude.include)
             .filter(ContextInclude.context == context))
    return (line.include for line in query)


def get_name_number(user_id):
    with session_scope() as session:
        query = (session.query(User.fullname.label('name'),
                               Extension.exten.label('exten'))
                 .join(UserLine.main_user_rel)
                 .join(LineExtension, UserLine.line_id == LineExtension.line_id)
                 .join(LineExtension.main_extension_rel)
                 .filter(User.id == user_id))
        row = query.first()
        if not row:
            raise LookupError('Cannot find a line from this user id %s' % user_id)
        return row.name, row.exten


def get_device_id(user_id):
    with session_scope() as session:
        query = (session.query(Line.device)
                 .join(UserLine.main_line_rel)
                 .join(UserLine.main_user_rel)
                 .filter(UserLine.user_id == user_id))
        result = query.scalar()
    if not result:
        raise LookupError('Cannot find a device from this user id %s' % user_id)
    return result


def get_user_config(user_id):
    with session_scope() as session:
        query = _config_query(session).filter(User.id == user_id)
        row = query.first()
        if not row:
            raise LookupError('No user with ID {}'.format(user_id))
        return {str(row.id): _format_row(row)}


def get_users_config():
    with session_scope() as session:
        query = _config_query(session)
        return {str(row.id): _format_row(row) for row in query}


def _config_query(session):
    columns = (getattr(User, name).label(name) for name in USER_CONFIG_FIELDS)
    return (session.query(Line.id.label('line_id'),
                          Line.context.label('line_context'),
                          Infos.uuid.label('xivo_uuid'),
                          *columns)
            .outerjoin(User.main_line_rel)
            .outerjoin(UserLine.linefeatures))


def _find_all_secondary_line_ids(user_id):
    with session_scope() as session:
        user_lines = session.query(UserLine.line_id).filter(UserLine.user_id == user_id,
                                                            UserLine.main_line == False).all()  # noqa
        return [str(line_id) for line_id, in user_lines]


def _format_row(row):
    main_line = row.line_id
    if main_line is None:
        line_ids = tuple()
    else:
        line_ids = (str(main_line),) + tuple(_find_all_secondary_line_ids(row.id))

    user = {name: getattr(row, name) for name in USER_CONFIG_FIELDS}
    user['identity'] = row.fullname
    user['context'] = row.line_context
    user['linelist'] = line_ids
    user['xivo_uuid'] = row.xivo_uuid
    return user
