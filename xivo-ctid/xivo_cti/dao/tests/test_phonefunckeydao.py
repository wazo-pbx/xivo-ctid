import unittest
from xivo_cti.dao.alchemy import dbconnection
from xivo_cti.dao.alchemy.base import Base
from xivo_cti.dao.alchemy.phonefunckey import PhoneFunckey
from xivo_cti.dao.phonefunckeydao import PhoneFunckeyDAO


class TestPhoneFunckey(unittest.TestCase):

    def setUp(self):
        self._user_id = 19
        self._destination = '123'
        db_connection_pool = dbconnection.DBConnectionPool(dbconnection.DBConnection)
        dbconnection.register_db_connection_pool(db_connection_pool)

        uri = 'postgresql://asterisk:asterisk@localhost/asterisktest'
        dbconnection.add_connection_as(uri, 'asterisk')
        connection = dbconnection.get_connection('asterisk')

        Base.metadata.drop_all(connection.get_engine(), [PhoneFunckey().__table__])
        Base.metadata.create_all(connection.get_engine(), [PhoneFunckey().__table__])

        self.session = connection.get_session()

        self._insert_funckeys()

        self.session.commit()

    def tearDown(self):
        dbconnection.unregister_db_connection_pool()

    def _insert_funckeys(self):
        fwd_unc = PhoneFunckey()
        fwd_unc.iduserfeatures = self._user_id
        fwd_unc.fknum = 2
        fwd_unc.exten = self._destination
        fwd_unc.typeextenumbers = 'extenfeatures'
        fwd_unc.typevalextenumbers = 'fwdunc'
        fwd_unc.supervision = 1
        fwd_unc.progfunckey = 1

        self.session.add(fwd_unc)

    def test_get_destination(self):
        dao = PhoneFunckeyDAO(self.session)

        reply = dao.get_dest_unc(self._user_id)

        self.assertEqual(reply, self._destination)
