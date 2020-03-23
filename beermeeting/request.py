import socketserver
from beermetting.packet import Packet
from beermetting.user import User
from beermetting.user import UserDao
import cx_Oracle
import pickle


class EchoRequestHandler(socketserver.BaseRequestHandler):
    """
    Clase para gestionar las peticiones al servidor TCP principal. En esta clase se encuentran los metodos para guardar
    los usuarios, gestionar los mensajes y verificar las operaciones solicitadas por los clientes.

    Methods
    -------
    read_packet()
        Esta función permite obtener los paquetes enviados al servidor. Escucha las peticiones de los clientes.
    handle_error(username: str, error)
        Función que gestionar los errores cuando el sistema tiene comportamientos no esperados
    handle_packets(decode: Packet)
        Controla los paquetes entrantes y los tramita según la función que realizan en la aplicación
    handle_operations(decode: Packet)
        Gestiona la operación a realizar en el momento que llega un paquete que tramita una operación en el servidor
    handle()
        Método principal que es sobreescrito de la clase BaseRequestHandler para gestionar los peticiones entrantes al
        servidor TCP
    """
    
    SOCKETS_LIST = []
    ACTIVE_USERS = []
    TOKEN = "DFGHJKLK"

    def read_packet(self) -> Packet:
        """
        Función para leer los paquetes entrantes
        Returns
        -------
        Packet
            Paquete resultante de la petición
        """
        data = self.request.recv(1024)
        return pickle.loads(data)
    
    def handle_error(self, username: str, error):
        """
        Función para controlar los errores en el servidor

        Parameters
        ----------
        username
            Usuario en el cual se presento el error
        error
            Error en el sistema

        """
        print("Excepción en el servidor")
        print(error)
        try:
            self.SOCKETS_LIST.remove(self.request)
            us = next(filter(lambda usr: usr.username == username, self.ACTIVE_USERS), None)
            self.ACTIVE_USERS.remove(us)
        except ValueError as error_exp:
            print(error_exp)
            
    def handle_packets(self, decode: Packet):
        """
        Función para manejar los paquetes en el servidor, esta función se encarga de manejar los posibles casos
        de respuesta del servidor

        Parameters
        ----------
        decode
            Paquete decodificado

        """
        if decode.packet_type == Packet.SERVER_REGISTER and decode.usr is not None:
            self.process_new_user(decode)
        elif decode.packet_type == Packet.SERVER_OPERATION and decode.usr is not None:
            self.handle_operations(decode)
        else:
            p = Packet.get_server_packet(Packet.SERVER_RESPONSE,
                                         "Debe encontrarse registrado antes de enviar peticiones")
            self.request.sendall(p)
    
    def handle_operations(self, decode: Packet):
        """
        Función para manejar las operaciones solicitadas por los clientes en el servidor

        Parameters
        ----------
        decode
            Paquete decodificado

        """
        if decode.op == Packet.OP_GET:
            decode.info = self.get_users()
            self.request.sendall(pickle.dumps(decode))
        elif decode.op == Packet.OP_BROADCAST:
            decode.packet_type = Packet.SERVER_RESPONSE
            self.broadcast_packet(decode, self.request)

    def handle(self):
        """
        Función que maneja las peticiones que solicitan los clientes, esta función recibe los paquetes entrantes del
        cliente y los procesa según la solicitud

        """
        p = Packet.get_server_packet(Packet.SERVER_RESPONSE, "Bienvenido al chat - registrate para iniciar\r\n")
        self.request.sendall(pickle.dumps(p))
        while True:
            decode = self.read_packet()
            try:
                if isinstance(decode, Packet):
                    if decode.packet_type == Packet.SERVER_EXIT:
                        self.handle_error(decode.usr.username, "Finalizar sessión " + self.client_address)
                    else:
                        self.handle_packets(decode)
                else:
                    p = Packet.get_server_packet(Packet.SERVER_ERROR, "Error en la petición")
                    self.request.sendall(p)
            except ValueError as error:
                self.handle_error(decode.usr.username, error)
                break
            except cx_Oracle.DatabaseError as error:
                self.handle_error(decode.usr.username, error)
                break
            except OSError as error:
                self.handle_error(decode.usr.username, error)
                break

    def process_new_user(self, decode):
        """
        Función para procesar un nuevo usuario, esta función se encarga de gestionar el TOKEN de verificación y
        determinar si el usuario ya se encuentra registrado.

        Parameters
        ----------
        decode
            Paquete decodificado con el usuario

        """
        usr = decode.usr
        usr.TOKEN = self.TOKEN
        self.fill_user(self.client_address, usr)
        decode.usr = self.register_user(decode.usr)
        self.notify_new_user(decode)

    def notify_new_user(self, decode):
        """
        Función para notificar al usuario el estado de su transacción, también notifica a los demás clientes de la
        conexión de un nuevo usuario

        Parameters
        ----------
        decode
            Paquete decodificado

        """
        self.SOCKETS_LIST.append(self.request)
        self.ACTIVE_USERS.append(decode.usr)
        new_client = Packet.get_server_packet(Packet.SERVER_RESPONSE, "Nuevo usuario conectado")
        self.broadcast_packet(new_client, self.request)
        self.request.sendall(pickle.dumps(decode))

    @staticmethod
    def register_user(usr: User) -> User:
        """
        Registra un nuevo usuario en la base de datos o en su defecto actualiza los datos del usuario según los
        parámetros de entrada

        Parameters
        ----------
        usr
            Usuario que ingresa al sistema

        Returns
        -------
        Usuario

        """
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
        """
        Obtiene todos los usuarios activos en el sistema

        Returns
        -------
        [User] Arreglo de usuarios activos en el sistema

        """
        return EchoRequestHandler.ACTIVE_USERS

    @staticmethod
    def fill_user(client_address, usr: User):
        """
        Ingresa los parámetros internos que gestiona el servidor

        Parameters
        ----------
        client_address
            Dirección del usuario en el sistema
        usr
            Usuario que ingresa la sistema

        """
        host, port = client_address
        usr.ip = host
        usr.port = port + 1

    @staticmethod
    def broadcast_string(b_msg, skip_socket):
        """
        Implementa un método para transferencia multiple string en el sistema

        Parameters
        ----------
        b_msg
            Mensaje a ser enviado
        skip_socket
            Socket ignorado en el proceso de envío

        Returns
        -------

        """
        for sock in EchoRequestHandler.SOCKETS_LIST:
            if sock != skip_socket:
                sock.sendall(b_msg.encode('UTF-8'))
        print(b_msg)

    @staticmethod
    def broadcast_packet(p_msg, skip_socket):
        """
        Implementa un método para transferencia multiple de paquetes en el sistema

        Parameters
        ----------
        p_msg
            Paquete a ser enviado
        skip_socket
            Socket ignorado en el proceso de envío

        Returns
        -------

        """
        for sock in EchoRequestHandler.SOCKETS_LIST:
            if sock != skip_socket:
                sock.sendall(pickle.dumps(p_msg))
