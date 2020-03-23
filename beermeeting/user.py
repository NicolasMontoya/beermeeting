from beermeeting.database import Database


class User:
    """
    Clase que modela los datos usuarios de un cliente, mediante está clase se comparte la información útil de un usuario
    en la aplicación.

    Methods
    -------

    get_ip_int()
        Obtiene la IP de la persona como un número entero

    """
    def __init__(self, ip, name, age, location, username, sex, port=29000):
        self.__ip = ip
        self.__port = port
        self.__name = name
        self.__username = username

        self.token = None
        self.sex = sex
        self.age = age
        self.location = location

    def get_ip_int(self) -> int:
        array = self.__ip.split('.')
        res = 0
        for i in range(len(array)):
            res = res + (int(array[i]) << (8 * i))
        return res

    @property
    def ip(self) -> str:
        return self.__ip

    @property
    def port(self) -> int:
        return self.__port

    @property
    def name(self) -> str:
        return self.__name

    @property
    def username(self):
        return self.__username

    @ip.setter
    def ip(self, ip: str):
        if isinstance(ip, str) and len(ip.split('.')) > 0:
            self.__ip = ip
        else:
            raise ValueError("Error, ingresar una IP correcta")

    @port.setter
    def port(self, port: int):
        if 8000 < port < 300000:
            self.__port = port
        else:
            raise ValueError("Error, ingresar una puerto correcto")

    def __str__(self):
        return  f"USUARIO: {self.username} -> \n NOMBRE: {self.name} SEXO: {self.sex} EDAD: {self.age}"

    def __repr__(self):
        return  f"USUARIO: {self.username} -> \n NOMBRE: {self.name} SEXO: {self.sex} EDAD: {self.age}"


class UserDao:
    """
    Clase para gestionar la persistencia de los datos de un usuario. Actualmente funciona con el driver cx_oracle y
    la clase de acceso Database

    Other Parameters
    ----------
    get_users_query
        Query para obtener todos los usuarios
    get_user_query
        Query para buscar un usuario mediante su nombre de usuario
    insert_user_query
        Query para insertar un usuario
    update_user_query
        Query para actualizar un usuario

    Methods
    -------
    get_users()
        Obtiene todos los usuarios de la base de datos
    get_user(username)
        Busca un usuario en la base de datos con el nombre de usuario indicado
    save_user(usr: User)
        Crea un nuevo usuario de base de datos
    update_user(usr: User)
        Actualiza un usuario de base de datos

    """

    get_users_query = "SELECT IP, NAME, AGE, LOCATION, USERNAME, SEX, PORT FROM BEER_USERS"
    get_user_query = "SELECT IP, NAME, AGE, LOCATION, USERNAME, SEX, PORT FROM BEER_USERS WHERE USERNAME = :username"
    insert_user_query = "INSERT INTO BEER_USERS (IP, NAME, AGE, SEX, LOCATION, USERNAME, PORT) VALUES (:ip, :name, " \
                        ":age, :sex, :loc, :username, :port)"
    update_user_query = "UPDATE BEER_USERS set IP = :ip, NAME = :name, AGE = :age, LOCATION = :loc, SEX = : SEX" \
                        ", PORT = :port WHERE USERNAME = :username"

    def __init__(self):
        self.__database: Database = Database.get_instance()

    def get_users(self) -> [User]:
        """
        Consulta todos los usuarios de la base de datos

        Returns
        -------
        [User]

        """
        rows = self.__database.query(self.get_users_query)
        users = []
        for row in rows:
            users.append(User(row[0], row[1], row[2], row[3], row[4], row[5], row[6]))
        return users

    def get_user(self, username) -> User:
        """
        Consulta un usuario de base de datos que tenga el nombre de usuario indicado

        Parameters
        ----------
        username
            Nombre de usuario para ser buscado

        Returns
        -------
        User

        """
        self.__database.execute(self.get_user_query, {'username': username})
        row = self.__database.fetchone()
        return User(row[0], row[1], row[2], row[3], row[4], row[5], row[6]) if row is not None else None

    def save_user(self, usr: User):
        """
        Guarda un nuevo usuario en la base de datos

        Parameters
        ----------
        usr
            Usuario a ser guardado

        """
        self.__database.execute(self.insert_user_query,
                                {'ip': usr.ip, 'name': usr.name, 'loc': usr.location, 'age': usr.age, 'sex': usr.sex,
                                 'username': usr.username, 'port': usr.port})
        self.__database.commit()

    def update_user(self, usr: User):
        """
        Actualiza un usuario en la base de datos

        Parameters
        ----------
        usr
            Usuario a ser actualizado

        """
        self.__database.execute(self.update_user_query,
                                {'ip': usr.ip, 'name': usr.name, 'loc': usr.location, 'age': usr.age, 'sex': usr.sex,
                                 'username': usr.username, 'port': usr.port})
        self.__database.commit()
