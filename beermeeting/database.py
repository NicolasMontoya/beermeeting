import cx_Oracle
import sqlite3


class Database:

    __instance = None

    @staticmethod
    def get_instance(username='', password='', dsn='', encoding='UTF-8', database_type=1):
        if Database.__instance is None:
            if database_type == 1 and username is not None and password is not None and dsn is not None:
                Database.__instance = DatabaseOracle(username, password, dsn, encoding)
            elif database_type == 2 and dsn is not None:
                Database.__instance = DatabaseLite(dsn)
            else:
                raise Exception("Ingrese los valores correctos ")
        return Database.__instance


class DatabaseOracle:
    """
    Clase para gestionar la conexión a la base de datos mediante el driver cx_oracle. Esta clase fue modelada con el
    patrón de diseño singleton para poder acceder desde un solo punto a la base de datos.

    Methods
    -------
    get_instance(username='', password='', dsn='', encoding='UTF-8')
        Función para obtener la instancia de la clase Database
    cursor()
        Retorna el cursor con el cual se realizan las operación en la DB
    commit()
        Permite realizar un commit de las transacciones realizadas en la db
    execute(sql, params=None)
        Ejecuta una query con los parámetros definidos
    fetchall()
        Obtiene los datos gestionados en el cursor
    fetchone()
        Obtiene un solo dato del cursor
    query()
        Ejecuta una query y retorna los datos obtenidos en el cursor

    """

    def __init__(self, username, password, dsn, encoding='UTF-8'):
        self.__db = cx_Oracle.connect(username, password, dsn, encoding=encoding)
        self.__db.autocommit = False
        self.__cursor = self.__db.cursor()
        Database.__instance = self

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


class DatabaseLite:
    """
    Clase para gestionar la conexión a la base de datos mediante el driver cx_oracle. Esta clase fue modelada con el
    patrón de diseño singleton para poder acceder desde un solo punto a la base de datos.

    Methods
    -------
    get_instance(username='', password='', dsn='', encoding='UTF-8')
        Función para obtener la instancia de la clase Database
    cursor()
        Retorna el cursor con el cual se realizan las operación en la DB
    commit()
        Permite realizar un commit de las transacciones realizadas en la db
    execute(sql, params=None)
        Ejecuta una query con los parámetros definidos
    fetchall()
        Obtiene los datos gestionados en el cursor
    fetchone()
        Obtiene un solo dato del cursor
    query()
        Ejecuta una query y retorna los datos obtenidos en el cursor

    """

    def __init__(self, url):
        self.__db = sqlite3.connect(url)
        self.__cursor = self.__db.cursor()
        DatabaseLite.__instance = self

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
