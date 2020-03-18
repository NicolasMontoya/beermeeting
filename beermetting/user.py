from beermetting.database import Database


class User:
    def __init__(self, ip, name, age, location):
        self.__ip = ip
        self.__name = name
        self.__age = age
        self.__location = location
        self.token = None

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
    def name(self) -> str:
        return self.__name

    @property
    def age(self) -> int:
        return self.__age

    @property
    def location(self):
        return self.__location

    @ip.setter
    def ip(self, ip: str):
        if isinstance(ip, str) and len(ip.split('.')) > 0 :
            self.__ip = ip
        else:
            raise ValueError("Error, ingresar una IP correcta")

    @age.setter
    def age(self, age):
        if age < 18:
            raise ValueError("Error, debe ser mayor de edad")
        self.__age = age


class UserDao:
    def __init__(self):
        self.__database : Database = Database.get_instance()

    def get_users(self) -> [User]:
        rows = self.__database.query("SELECT IP, NAME, AGE, LOCATION FROM BEER_USERS")
        users = []
        for row in rows:
            users.append(User(row[0], row[1], row[2], row[3]))
        return users
