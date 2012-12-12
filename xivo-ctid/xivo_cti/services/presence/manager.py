# -*- coding: utf-8 -*-


class PresenceServiceManager(object):
    def __init__(self, innerdata_dao):
        self._innerdata_dao = innerdata_dao

    def is_valid_presence(self, profile, presence):
        presences = self._innerdata_dao.get_presences(profile)
        return presence in presences
