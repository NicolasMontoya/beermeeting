import pickle
import socket
import time
import threading
from beermeeting.packet import Packet
from beermeeting.user import User
from socketserver import ThreadingUDPServer, BaseRequestHandler


class Client:
    """
    Clase usada para gestionar los clientes de la aplicación beermeting. Hace parte de dicho modulo y permite
    gestionar la conexión con el servidor TCP, además internamente permite crear hilos para gestionar un servidor
    UDP y para recibir información de manera asincrona.

    ...

    Methods
    -------
    read_packets_thread(conn: SocketConnection, stop_thread: boolean)
        Función que permite leer los mensajes de iterativa. Puede usarse con hilos
    read
        lectura de paquete
    read_packet(conn)
        Permite leer mensajes enviados por el servidor TCP
    open_connection()
        Abre la conexión con el socket TCP
    send_packet()
        Envia un objeto de la clase Packet al servidor TCP
    send_and_wait()
        Envia un objeto de la clase Packet al servidor TCP y espera la respuesta del servidor
    close_connection()
        Cierra la conexión con el socket TCP
    register_user(username: str, name: str = None, age: int = None, sex: str = None, location: str = None)
        Registra o logea un usuario en el servidor principal. Si se un usuario ya existente el sistema actualiza los
        datos, NOTA: Si se envía un usuario que no existe en la base de datos y no lleva la información completa el
        sistema retorna error
    get_active_users()
        Solicita al servidor los usuarios activos en la aplicación
    waiting_user()
        Espera hasta que el cliente tenga un usuario activo (Sirve para trabajar con hilos)
    create_udp_server()
        Crea un servidor UDP gestionado por el cliente
    open_udp_server()
        Inicia el hilo donde se creo el servidor UDP
    close_udp_server()
        Cierra el servidor UDP y finaliza el hilo
    send_message_manual(info)
        Gestiona el envío de mensajes mediante entradas del usuario (usa la función input)
    send_message(info)
        Gestiona el envío de mensajes de manera automática
    run()
        Inicialización del cliente para uso por consola
    """

    def __init__(self, host="localhost", port=9999):
        """
        Constructor del modulo

        Parameters
        ----------
        host
            Indica la IP en la cual se encuentra el servidor
        port
            Indica el puerto en cual se encuentra el servidor
        """
        # Inicializar los sockets necesarios para comunicación
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Inicializar variables para Threads - Sockets
        self.stop_threads = False
        self.read_thread = threading.Thread(target=self.read_packets_thread,
                                            args=(lambda: self.stop_threads,))
        self.udp_server_thread = None
        self.udp_server = None

        # Inicializar variables del cliente
        self.__host = host
        self.__port = port
        self.user = None
        self.error = None

        # Menu de la aplicación
        self.menu = Menu()
        # Usuarios en el servidor
        self.active_users = []

    def read_packets_thread(self, stop_thread):
        """
        Función que permite leer de manera iterativa los mensajes entrantes al clientes desde el servidor principal.
        Mediante esta función y el uso de hilo el cliente tiene en tiempo real los mensajes del servidor


        Parameters
        ----------
        stop_thread
            Booleano que sirve para parar el bucle infinito

        """
        while True:
            self.read_packet()
            if stop_thread():
                break

    # TODO: Mejorar el sistema de recepción para capturar el error de usuario inexistente
    def read_packet(self):
        """
        Función que permite leer los paquetes de tipo SERVER_REGISTER, SERVER_RESPONSE y SERVER_OPERATION provenientes
        del servidor. Este imprime en consola los datos de interes para el cliente.

        """

        data = self.socket.recv(1024)
        p = pickle.loads(data)
        print(self.process_packet(p))

    def process_packet(self, p):
        if p.packet_type == Packet.SERVER_REGISTER:
            self.user = p.usr
            return f"Ingreso con {self.user.username}"
        elif p.packet_type == Packet.SERVER_RESPONSE:
            return f"\n\r Mensaje público >>	{p.info}"
        elif p.packet_type == Packet.SERVER_OPERATION:
            if p.op == Packet.OP_GET:
                self.active_users = p.info
                return p.info
        elif p.packet_type == Packet.SERVER_ERROR:
            raise Exception(f"Error {p.info}")
        else:
            return p.info

    def read(self):
        """
        Función que permite leer los paquetes de tipo SERVER_REGISTER, SERVER_RESPONSE y SERVER_OPERATION provenientes
        del servidor. Este imprime en consola los datos de interes para el cliente.

        """

        data = self.socket.recv(1024)
        return pickle.loads(data)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_threads = True
        self.read_thread.join()
        self.close_connection()
        if self.udp_server is not None:
            self.udp_server.shutdown()
            self.udp_server.server_close()

    def open_connection(self):
        """
        Abre la conexión del socket que se conecta con el servidor principal

        """
        self.socket.connect((self.__host, self.__port))

    def send_packet(self, packet):
        """
        Envia paquetes al servidor principal, esta función hace uso del paquete picket para convertir objetos Python
        en bytes que puedan ser transmitidos por el socket

        Parameters
        ----------
        packet
            Paquete del sistema que contiene la solicitud a realizar.

        """
        data = pickle.dumps(packet)
        self.socket.sendall(data)

    def send_and_wait(self, packet):
        """
        Envia paquetes al servidor principal, esta función hace uso del paquete picket para convertir objetos Python
        en bytes que puedan ser transmitidos por el socket.

        Esta función tiene la particularidad que permite enviar y esperar la respuesta del servidor

        Parameters
        ----------
        packet
            Paquete del sistema que contiene la solicitud a realizar.

        """
        self.send_packet(packet)
        res = self.socket.recv(1024)
        return res

    def close_connection(self):
        """
        Cierra la conexión del socket

        """
        self.socket.close()

    def register_user(self, username: str, name: str = None, age: int = None, sex: str = None, location: str = None):
        """
        Registra un usuario en el sistema principal para que sea accesible por los demás usuarios en el sistema

        Parameters
        ----------
        username Nombre de usuario en la plataforma
        name (OPCIONAL) Nombre de la persona que se registra
        age (OPCIONAL) Edad de la persona que se registra
        sex (OPCIONAL) Sexo de la persona que se registra
        location (OPCIONAL) Lugar donde vive la persona que se registra

        """
        usr = User(None, name, age, location, username, sex)
        self.send_packet(Packet(Packet.SERVER_REGISTER, None, None, '', usr))

    def get_active_users(self):
        """
        Solicita al servidor los usuarios activos en la aplicación

        """
        p = Packet.get_client_packet(Packet.SERVER_OPERATION, None, self.user)
        p.op = Packet.OP_GET
        self.send_packet(p)

    def waiting_user(self):
        """
        Función que espera que el usuario sea aceptado por el servidor principal para continuar con el hilo principal

        """
        print("Cargando...", end='')
        while True:
            time.sleep(1)
            print('.', end='')
            if self.user is not None:
                break
            if self.error is not None:
                exit()

    def create_udp_server(self):
        """
        Crea un servidor UDP en un hilo externo para recibir los mensajes punto a punto de la aplicación. Es decir,
        una vez registrado en la aplicación el cliente puede recibir mensajes directamente mediante este servidor

        """
        self.udp_server = ThreadingUDPServer((self.user.ip, self.user.port),
                                             ThreadedUDPRequestHandler)
        self.udp_server_thread = threading.Thread(target=self.udp_server.serve_forever)
        self.udp_server_thread.daemon = True

    def open_udp_server(self):
        """
        Abre el servidor UDP del cliente

        """
        if self.udp_server is None:
            self.create_udp_server()
        self.udp_server_thread.start()

    def close_udp_server(self):
        """
        Cierra el servidor UDP del cliente

        """
        self.user = None
        self.udp_server.shutdown()
        self.udp_server.server_close()
        self.udp_server_thread.join()

    def send_message_manual(self, info):
        """
        Envia mensajes según las opciones elegidas, puede realizar un envío del paquete mediante TCP o UDP según el
        destinatario. Si el destinatario está vacío el envío se realiza para como mensaje BROADCAST hacía el servidor

        Parameters
        ----------
        info
            Información para realizar el envío del paquete.

            - UDP
            [0] -> Contiene la operación a realizar
            [1] -> Contiene el username del destinatario

            - TCP
            [0] -> Contiene la operación a realizar

        """
        if len(info) == 2:
            p = next(filter(lambda dst_user: dst_user.username == info[1], self.active_users),
                     None)
            if p is not None:
                msg = input()
                p_send = Packet.get_client_packet(Packet.SEND_DATA, msg, self.user)
                self.sock.sendto(pickle.dumps(p_send), (p.ip, p.port))
                print("Mensaje enviado.")
            else:
                print("No encontramos el usuario, recargue los usuarios activos")
        elif len(info) == 1:
            msg = input('>>')
            p = Packet.get_client_packet(Packet.SERVER_OPERATION, msg, self.user)
            p.op = Packet.OP_BROADCAST
            self.send_packet(p)
            print("Mensaje enviado.")
        else:
            print("No integrso las opciones correctas")

    def send_message(self, info):
        """
        Envia mensajes según las opciones elegidas, puede realizar un envío del paquete mediante TCP o UDP según el
        destinatario. Si el destinatario está vacío el envío se realiza para como mensaje BROADCAST hacía el servidor

        Parameters
        ----------
        info
            Información para realizar el envío del paquete.

            - UDP
            [0] -> Contiene la operación a realizar
            [1] -> Contiene el username del destinatario
            [2] -> Contiene el mensaje a ser enviado

            - TCP
            [0] -> Contiene la operación a realizar
            [1] -> Contiene el mensaje a ser enviado

        """
        if len(info) == 3:
            p = next(filter(lambda dst_user: dst_user.username == info[1], self.active_users),
                     None)
            if p is not None:
                p_send = Packet.get_client_packet(Packet.SEND_DATA, info[2], self.user)
                self.sock.sendto(pickle.dumps(p_send), (p.ip, p.port))
                print("Mensaje enviado.")
            else:
                print("No encontramos el usuario, recargue los usuarios activos")
        elif len(info) == 2:
            p = Packet.get_client_packet(Packet.SERVER_OPERATION, info[1], self.user)
            p.op = Packet.OP_BROADCAST
            self.send_packet(p)
            print("Mensaje enviado.")
        else:
            print("No integrso las opciones correctas")

    def run(self):
        """
        Función que gestiona las operaciones del cliente mediante la consola de Python.


        """
        self.open_connection()
        self.read_thread.start()
        self.menu.show('HOME')
        while True:
            request = input(">>	")
            if self.menu.is_option(request):
                if request == 'ENTRAR':
                    user_data = input("Ingrese datos separados por | (USERNAME|NAME|AGE|SEX|LOCATION)")
                    config_user = user_data.split("|")
                    if len(config_user) == 5 or len(config_user) == 1:
                        try:
                            self.register_user(config_user[0], config_user[1], int(config_user[2]), config_user[3],
                                               config_user[4])
                        except IndexError:
                            self.register_user(config_user[0])
                        self.waiting_user()

                        self.create_udp_server()
                        self.open_udp_server()
                        print("Conexión correcta ")

                        self.menu.show('APP')
                        while True:
                            request = input()
                            if request == 'ATRAS':
                                self.close_udp_server()
                                break
                            elif request == 'USUARIOS':
                                self.get_active_users()
                            elif 'MSG' in request:
                                msg = request.split("|")
                                self.send_message_manual(msg)
                    else:
                        print("Datos incorrectos. Ingrese correctamente los datos solicitados")
                if request == 'SALIR':
                    break
            else:
                print("-> Opción incorrecta")


class ThreadedUDPRequestHandler(BaseRequestHandler):
    """
    Clase encargada gestionar las peticiones al servidor UDP propio de los clientes, su función permite leer el paquete
    enviado y extraer el usuario y la infomación que contiene el paquete.

    Methods
    -------
    handle()
        Función que recibe los paquetes cuando son enviados desde el cliente

    """

    def handle(self):
        data: Packet = pickle.loads(self.request[0])
        print(f"Mensaje de {data.usr.username} >> {data.info}")


class Menu:
    """
    Menu en consola que permite a los usuarios reconocer el uso del sistema. La clase almacena el menu dentro de la app
    y el menu de HOME.

    Methods
    -------
    show()
        Impresión del menú en consola

    """
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
