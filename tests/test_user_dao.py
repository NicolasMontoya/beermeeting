import unittest
from beermeeting.database import Database
from beermeeting.user import UserDao
import config


class TestUserDao(unittest.TestCase):

    def setUp(self) -> None:
        Database.get_instance(config.username, config.password, config.dsn)
        self.user_dao = UserDao()

    def test_get_users(self):
        users = self.user_dao.get_users()
        self.assertGreater(len(users), 0)

    def test_get_user(self):
        user = self.user_dao.get_user('NIET')
        self.assertIsNotNone(user)

    def test_get_none(self):
        user = self.user_dao.get_user('PRUEBA')
        self.assertIsNone(user)


if __name__ == '__main__':
    unittest.main()
