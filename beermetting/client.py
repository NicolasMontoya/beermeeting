import pickle
import socket
import time
import threading
from beermetting.packet import Packet
from beermetting.user import User


class Client:
    cache = []

    def __init__(self, host="localhost", port=9999, socket_type=1):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__host = host
        self.__port = port
        self.socket_type = socket_type
        self.stop_threads = False
        self.readThread = threading.Thread(target=self.read_messages, args=(self.socket, lambda: self.stop_threads))
        self.menu = Menu()
        self.user = None

    def read_messages(self, conn, stop_thread):
        while True:
            data = conn.recv(1024)
            print("")
            p = pickle.loads(data)
            if p.usr is not None:
                self.user = p.usr
                print(self.user.name)
            if p.packet_type == 2:
                print("\n\r Mensaje entrante > " + p.src.name + ">	dice -> " + p.info)
                print("> ")
            else:
                print(p.info)
            if stop_thread():
                break

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_threads = True
        self.readThread.join()
        self.close_connection()

    def open_connection(self):
        self.socket.connect((self.__host, self.__port))

    def send(self, packet):
        data = pickle.dumps(packet)
        self.socket.send(data)

    def send_and_wait(self, packet):
        self.send(packet)
        res = self.socket.recv(1024)
        return res

    def close_connection(self):
        self.socket.close()

    def run(self):
        self.open_connection()
        self.readThread.start()
        self.menu.show()
        while True:
            request = input(">>	")
            if self.menu.is_option(request):
                if request == 'ENTRAR':
                    user_data = input("Ingrese datos separados por |")
                    config_user = user_data.split("|")
                    if len(config_user) == 4:
                        self.user = User(None, config_user[0], int(config_user[1]), config_user[2])
                        self.socket.sendall(pickle.dumps(Packet(1, None, None, '', self.user)))
                    else:
                        print("Datos incorrectos. Ingrese correctamente los datos solicitados")
                if request == 'SALIR':
                    break
            else:
                print("-> Opción incorrecta")


class Menu:
    OPTIONS_HOME = ['ENTRAR', 'SALIR']

    def __init__(self):
        self.open = False

    def show(self):
        print("----------------------")
        print("---------MENU---------")
        for option in self.OPTIONS_HOME:
            print(">> " + option)
        print(" ---------------------")
        print("")
        time.sleep(1)

    def is_option(self, request) -> bool:
        return next((option for option in self.OPTIONS_HOME if option == request), None) is not None
