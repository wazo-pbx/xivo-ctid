import logging

from xivo_cti.dao.alchemy.userfeatures import UserFeatures
from xivo_cti.dao.alchemy import dbconnection

logger = logging.getLogger("UserFeaturesDAO")


class UserFeaturesDAO(object):

    def __init__(self, session):
        self._session = session

    def enable_dnd(self, user_id):
        self._session.query(UserFeatures).filter(UserFeatures.id == user_id).update({'enablednd': 1})
        self._session.commit()
        self._innerdata.xod_config['users'].keeplist[user_id]['enablednd'] = True

    def disable_dnd(self, user_id):
        self._session.query(UserFeatures).filter(UserFeatures.id == user_id).update({'enablednd': 0})
        self._session.commit()
        self._innerdata.xod_config['users'].keeplist[user_id]['enablednd'] = False

    def enable_filter(self, user_id):
        self._session.query(UserFeatures).filter(UserFeatures.id == user_id).update({'incallfilter': 1})
        self._session.commit()
        self._innerdata.xod_config['users'].keeplist[user_id]['incallfilter'] = True

    def disable_filter(self, user_id):
        self._session.query(UserFeatures).filter(UserFeatures.id == user_id).update({'incallfilter': 0})
        self._session.commit()
        self._innerdata.xod_config['users'].keeplist[user_id]['incallfilter'] = False

    def enable_unconditional_fwd(self, user_id, destination):
        self._session.query(UserFeatures).filter(UserFeatures.id == user_id).update({'enableunc': 1,
                                                                                     'destunc': destination})
        self._session.commit()
        self._innerdata.xod_config['users'].keeplist[user_id]['enableunc'] = True
        self._innerdata.xod_config['users'].keeplist[user_id]['destunc'] = destination

    def disable_unconditional_fwd(self, user_id, destination):
        self._session.query(UserFeatures).filter(UserFeatures.id == user_id).update({'enableunc': 0,
                                                                                     'destunc': destination})
        self._session.commit()
        self._innerdata.xod_config['users'].keeplist[user_id]['destunc'] = destination
        self._innerdata.xod_config['users'].keeplist[user_id]['enableunc'] = False

    def enable_rna_fwd(self, user_id, destination):
        self._session.query(UserFeatures).filter(UserFeatures.id == user_id).update({'enablerna': 1,
                                                                                     'destrna': destination})
        self._session.commit()
        self._innerdata.xod_config['users'].keeplist[user_id]['enablerna'] = True
        self._innerdata.xod_config['users'].keeplist[user_id]['destrna'] = destination

    def disable_rna_fwd(self, user_id, destination):
        self._session.query(UserFeatures).filter(UserFeatures.id == user_id).update({'enablerna': 0,
                                                                                     'destrna': destination})
        self._session.commit()
        self._innerdata.xod_config['users'].keeplist[user_id]['destrna'] = destination
        self._innerdata.xod_config['users'].keeplist[user_id]['enablerna'] = False

    def enable_busy_fwd(self, user_id, destination):
        self._session.query(UserFeatures).filter(UserFeatures.id == user_id).update({'enablebusy': 1,
                                                                                     'destbusy': destination})
        self._session.commit()
        self._innerdata.xod_config['users'].keeplist[user_id]['enablebusy'] = True
        self._innerdata.xod_config['users'].keeplist[user_id]['destbusy'] = destination

    def disable_busy_fwd(self, user_id, destination):
        self._session.query(UserFeatures).filter(UserFeatures.id == user_id).update({'enablebusy': 0,
                                                                                     'destbusy': destination})
        self._session.commit()
        self._innerdata.xod_config['users'].keeplist[user_id]['destbusy'] = destination
        self._innerdata.xod_config['users'].keeplist[user_id]['enablebusy'] = False

    @classmethod
    def new_from_uri(cls, uri):
        connection = dbconnection.get_connection(uri)
        return cls(connection.get_session())
