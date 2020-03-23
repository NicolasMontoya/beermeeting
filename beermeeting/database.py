import cx_Oracle


class Database:
    """
    Clase para gestionar la conexión a la base de datos mediante el driver cx_oracle

    Methods
    -------
    get_instance(username='', password='', dsn='', encoding='UTF-8')
    """

    __instance = None

    @staticmethod
    def get_instance(username='', password='', dsn='', encoding='UTF-8'):
        """ Static access method. """
        if Database.__instance is None:
            Database(username, password, dsn, encoding)
        return Database.__instance

    def __init__(self, username, password, dsn, encoding='UTF-8'):
        if Database.__instance is None:
            self.__db = cx_Oracle.connect(username, password, dsn, encoding=encoding)
            self.__db.autocommit = False
            self.__cursor = self.__db.cursor()
            Database.__instance = self
        else:
            raise Exception("This class is a singleton!")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__cursor.close()
        self.__db.close()

    @property
    def cursor(self):
        return self.__cursor

    def commit(self):
        self.__db.commit()

    def execute(self, sql, params=None):
        return self.cursor.execute(sql, params or ())

    def fetchall(self):
        return self.cursor.fetchall()

    def fetchone(self):
        return self.cursor.fetchone()

    def query(self, sql, params=None):
        self.cursor.execute(sql, params or ())
        return self.fetchall()
