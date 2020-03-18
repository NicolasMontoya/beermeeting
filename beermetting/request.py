
import socketserver
from beermetting.packet import Packet
from beermetting.user import User

import pickle


SOCKETS_LIST = []
ACTIVE_USERS = []
TOKEN = "DFGHJKLK"


class EchoRequestHandler(socketserver.BaseRequestHandler):

    @staticmethod
    def broadcast_string(b_msg, skip_socket):
        for socket in SOCKETS_LIST:
            if socket != skip_socket:
                socket.sendall(b_msg.encode('UTF-8'))
        print(b_msg)

    @staticmethod
    def broadcast_packet(p_msg, skip_socket):
        for socket in SOCKETS_LIST:
            if socket != skip_socket:
                socket.sendall(pickle.dumps(p_msg))

    def handle(self):
        p = Packet.get_server_packet("Bienvenido al chat - registrate para iniciar\r\n")
        self.request.sendall(pickle.dumps(p))
        host, port = self.client_address
        while True:
            try:
                data = self.request.recv(1024)
                decode = pickle.loads(data)
                if decode == "bye":
                    msg = "Client left" + str(self.client_address) + "\r\n"
                    SOCKETS_LIST.remove(self.request)
                    self.broadcast_string(msg, self.request)
                    break
                else:
                    if isinstance(decode, Packet):
                        if decode.packet_type == 1 and decode.usr is not None:
                            decode.usr.token = TOKEN
                            print("ENTRO TOKEN")
                            SOCKETS_LIST.append(self.request)
                            new_client = Packet.get_server_packet("Nuevo usuario conectado")
                            self.broadcast_packet(new_client, self.request)
                            self.request.sendall(pickle.dumps(decode))
                        elif decode.packet_type == 2 and decode.usr is not None:
                            pass
                        else:
                            p = Packet.get_server_packet("Debe encontrarse registrado antes de enviar peticiones")
                            self.request.sendall(p)
                    else:
                        p = Packet.get_server_packet("Error en la petición")
                        self.request.sendall(p)
            except:
                print("An exception occurred")
                SOCKETS_LIST.remove(self.request)
                msg = "Client left" + str(self.client_address) + "\r\n"
                self.broadcast_string(msg, self.request)
