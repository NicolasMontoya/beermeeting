from beermetting.database import Database


class User:
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
    def __init__(self):
        self.__database: Database = Database.get_instance()

    def get_users(self) -> [User]:
        rows = self.__database.query("SELECT IP, NAME, AGE, LOCATION, USERNAME, SEX, PORT FROM BEER_USERS")
        users = []
        for row in rows:
            users.append(User(row[0], row[1], row[2], row[3], row[4], row[5], row[6]))
        return users

    def get_user(self, username) -> User:
        self.__database.execute("SELECT IP, NAME, AGE, LOCATION, USERNAME, SEX, PORT FROM BEER_USERS WHERE USERNAME = "
                                ":username", {'username': username})
        row = self.__database.fetchone()
        return User(row[0], row[1], row[2], row[3], row[4], row[5], row[6]) if row is not None else None

    def save_user(self, usr: User):
        self.__database.execute("INSERT INTO BEER_USERS (IP, NAME, AGE, SEX, LOCATION, USERNAME, PORT) VALUES"
                                " (:ip, :name, :age, :sex, :loc, :username, :port)",
                                {'ip': usr.ip, 'name': usr.name, 'loc': usr.location, 'age': usr.age, 'sex': usr.sex,
                                 'username': usr.username, 'port': usr.port})
        self.__database.commit()

    def update_user(self, usr: User):
        self.__database.execute("UPDATE BEER_USERS set IP = :ip, NAME = :name, AGE = :age, LOCATION = :loc, SEX = : SEX"
                                ", PORT = :port WHERE USERNAME = :username",
                                {'ip': usr.ip, 'name': usr.name, 'loc': usr.location, 'age': usr.age, 'sex': usr.sex,
                                 'username': usr.username, 'port': usr.port})
        self.__database.commit()
