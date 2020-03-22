import pickle
import socket
import time
import threading
from beermetting.packet import Packet
from beermetting.user import User
from socketserver import ThreadingUDPServer, BaseRequestHandler


class Client:
    cache = []

    def __init__(self, host="localhost", port=9999, socket_type=1):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__host = host
        self.__port = port
        self.socket_type = socket_type
        self.stop_threads = False
        self.readThread = threading.Thread(target=self.read_messages, args=(self.socket, lambda: self.stop_threads))
        self.menu = Menu()
        self.active_users = []
        self.user = None
        self.error = None
        self.udp_server = None

    def read_messages(self, conn, stop_thread):
        while True:
            data = conn.recv(1024)
            print("")
            p: Packet = pickle.loads(data)
            if p.packet_type == Packet.SERVER_REGISTER:
                print("\n\r Usuario entrante >>	")
                self.user = p.usr
            elif p.packet_type == Packet.SERVER_RESPONSE:
                print("\n\r Mensaje entrante >>	")
                print("> ")
                print(p.info)
            elif p.packet_type == Packet.SERVER_OPERATION:
                if p.op == Packet.OP_GET:
                    self.active_users = p.info
                    print(p.info)
            elif p.packet_type == Packet.SERVER_ERROR:
                print(p.info)

            else:
                print(p.info)
            if stop_thread():
                break

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_threads = True
        self.readThread.join()
        self.close_connection()
        if self.udp_server is not None:
            self.udp_server.shutdown()
            self.udp_server.server_close()

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
        self.menu.show('HOME')
        while True:
            request = input(">>	")
            if self.menu.is_option(request):
                if request == 'ENTRAR':
                    user_data = input("Ingrese datos separados por |")
                    config_user = user_data.split("|")
                    if len(config_user) == 5 or len(config_user) == 1:
                        usr = User(None, config_user[0], int(config_user[1]), config_user[2], config_user[3],
                                   config_user[4]) if len(config_user) == 5 else User(None, None, None,
                                                                                      None, config_user[0], None)
                        self.socket.sendall(pickle.dumps(Packet(Packet.SERVER_REGISTER, None, None, '', usr)))
                        print("Cargando...", end='')
                        while True:
                            time.sleep(1)
                            print('.', end='')
                            if self.user is not None:
                                break
                            if self.error is not None:
                                exit()

                        print("")
                        print(self.user)
                        print("Conexión correcta ")
                        self.udp_server = ThreadingUDPServer((self.user.ip, self.user.port),
                                                             ThreadedUDPRequestHandler)
                        server_thread = threading.Thread(target=self.udp_server.serve_forever)
                        server_thread.daemon = True
                        server_thread.start()
                        self.menu.show('APP')
                        while True:
                            request = input(">>	")
                            if request == 'ATRAS':
                                self.user = None
                                server_thread.join()
                                self.udp_server.shutdown()
                                self.udp_server.server_close()
                                break
                            elif request == 'USUARIOS':
                                p = Packet.get_client_packet(Packet.SERVER_OPERATION, None, self.user)
                                p.op = Packet.OP_GET
                                self.socket.sendall(
                                    pickle.dumps(p))
                            elif 'MSG' in request:
                                f = request.split("|")
                                if len(f) == 2:
                                    p = next(filter(lambda dst_user: dst_user.username == f[1], self.active_users), None)
                                    print("Mensaje enviado.")
                                    msg = input('>>')
                                    self.sock.sendto(msg.encode('UTF-8'), (p.ip, p.port))
                                elif len(f) == 1:
                                    msg = input('>>')
                                    p = Packet.get_client_packet(Packet.SERVER_OPERATION, msg, self.user)
                                    p.op = Packet.OP_BROADCAST
                                    self.socket.sendall(
                                        pickle.dumps(p))
                                else:
                                    print("No integrso las opciones correctas")

                    else:
                        print("Datos incorrectos. Ingrese correctamente los datos solicitados")
                if request == 'SALIR':
                    break
            else:
                print("-> Opción incorrecta")


class ThreadedUDPRequestHandler(BaseRequestHandler):

    def handle(self):
        data = self.request[0].strip()
        socket_udp = self.request[1]
        print(f"Mensaje de >> {data}")
        socket_udp.sendto(data.upper(), self.client_address)


class Menu:
    OPTIONS = {'HOME': ['ENTRAR', 'MENU', 'SALIR'], 'APP': ['MENU', 'USUARIOS', 'MSG', 'ATRAS']}

    def __init__(self):
        self.open = False

    def show(self, option_type):
        print("----------------------")
        print("---------MENU---------")
        for option in self.OPTIONS[option_type]:
            print(">> " + option)
        print(" ---------------------")
        print("")
        time.sleep(1)

    def is_option(self, request, option_type='HOME') -> bool:
        return next((option for option in self.OPTIONS[option_type] if option == request), None) is not None
