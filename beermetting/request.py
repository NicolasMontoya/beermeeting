import socketserver
from beermetting.packet import Packet
from beermetting.user import User
from beermetting.user import UserDao
import cx_Oracle
import socket

import pickle

SOCKETS_LIST = []
ACTIVE_USERS = []
TOKEN = "DFGHJKLK"


class EchoRequestHandler(socketserver.BaseRequestHandler):

    @staticmethod
    def broadcast_string(b_msg, skip_socket):
        for sock in SOCKETS_LIST:
            if sock != skip_socket:
                sock.sendall(b_msg.encode('UTF-8'))
        print(b_msg)

    @staticmethod
    def broadcast_packet(p_msg, skip_socket):
        for sock in SOCKETS_LIST:
            if sock != skip_socket:
                sock.sendall(pickle.dumps(p_msg))

    def handle(self):
        p = Packet.get_server_packet(Packet.SERVER_RESPONSE, "Bienvenido al chat - registrate para iniciar\r\n")
        self.request.sendall(pickle.dumps(p))
        while True:
            try:
                data = self.request.recv(1024)
                decode: Packet = pickle.loads(data)
                if isinstance(decode, Packet):
                    if decode.packet_type == Packet.SERVER_EXIT:
                        msg = "El cliente ha abandonado la sesión"
                        SOCKETS_LIST.remove(self.request)
                        us = filter(lambda usr: usr.username == decode.usr.username, ACTIVE_USERS)[0]
                        ACTIVE_USERS.remove(us)
                        p = Packet.get_server_packet(Packet.SERVER_RESPONSE, "Debe encontrarse registrado antes de enviar peticiones")
                        self.broadcast_packet(p, self.request)
                    else:
                        if decode.packet_type == Packet.SERVER_REGISTER and decode.usr is not None:
                            self.process_new_user(decode)
                        elif decode.packet_type == Packet.SERVER_OPERATION and decode.usr is not None:
                            if decode.op == Packet.OP_GET:
                                decode.info = self.get_users()
                                self.request.sendall(pickle.dumps(decode))
                            elif decode.op == Packet.OP_BROADCAST:
                                self.broadcast_packet()
                        else:
                            p = Packet.get_server_packet(Packet.SERVER_RESPONSE, "Debe encontrarse registrado antes de enviar peticiones")
                            self.request.sendall(p)
                else:
                    p = Packet.get_server_packet(Packet.SERVER_ERROR, "Error en la petición")
                    self.request.sendall(p)
            except ValueError as error:
                print("An exception occurred")
                msg = "Client left" + str(self.client_address) + "\r\n"
                try:
                    SOCKETS_LIST.remove(self.request)
                    us = filter(lambda usr: usr.username == decode.usr.username, ACTIVE_USERS)[0]
                    ACTIVE_USERS.remove(us)
                except ValueError:
                    msg = error
                p = Packet.get_server_packet(Packet.SERVER_ERROR, msg)
                self.request.sendall(pickle.dumps(p))
            except cx_Oracle.DatabaseError as error:
                print(error)
                print("An exception occurred")
                msg = "Client left" + str(self.client_address) + "\r\n"
                try:
                    SOCKETS_LIST.remove(self.request)
                    us = filter(lambda usr: usr.username == decode.usr.username, ACTIVE_USERS)[0]
                    ACTIVE_USERS.remove(us)
                except ValueError:
                    msg = error
                p = Packet.get_server_packet(Packet.SERVER_ERROR, msg)
                self.request.sendall(pickle.dumps(p))
            except OSError as error:
                print("An exception occurred")
                msg = "Client left" + str(self.client_address) + "\r\n"
                try:
                    SOCKETS_LIST.remove(self.request)
                    us = next(filter(lambda usr: usr.username == decode.usr.username, ACTIVE_USERS), None)
                    ACTIVE_USERS.remove(us)
                except ValueError:
                    msg = error
                break

    def process_new_user(self, decode):
        usr = decode.usr
        usr.token = TOKEN
        self.fill_user(self.client_address, usr)
        decode.usr = self.register_user(decode.usr)
        self.notify_new_user(decode)

    def notify_new_user(self, decode):
        SOCKETS_LIST.append(self.request)
        ACTIVE_USERS.append(decode.usr)
        new_client = Packet.get_server_packet(Packet.SERVER_RESPONSE, "Nuevo usuario conectado")
        self.broadcast_packet(new_client, self.request)
        self.request.sendall(pickle.dumps(decode))

    @staticmethod
    def register_user(usr: User) -> User:
        us = UserDao()
        in_db = us.get_user(usr.username)
        print(in_db)
        if in_db is None:
            us.save_user(usr)
            in_db = usr
        else:
            in_db.port = usr.port
            in_db.ip = usr.ip
            us.update_user(in_db)
        return in_db

    @staticmethod
    def get_users() -> [User]:
        return ACTIVE_USERS

    @staticmethod
    def fill_user(client_address, usr: User):
        host, port = client_address
        usr.ip = host
        usr.port = port + 1



