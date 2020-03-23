class Packet:
    """
    Unidad básica de información en el sistema de beermeeting, esta clase permite gestionar la información en las
    peticiones realizadas entre los diferentes socket.

    Methods
    -------
    get_client_packet(packet_type, msg=None, usr=None)
        Esta función permite generar un paquete estático en el cliente con la información base que este necesita.
    get_server_packet(packet_type, msg=None, usr=None)
        Esta función permite generar un paquete estático en el servidor con la información base que este necesita.
    """
    SERVER_REGISTER = 1
    SERVER_OPERATION = 2
    SERVER_RESPONSE = 3
    SERVER_ERROR = 4
    SERVER_EXIT = 5
    SEND_DATA = 6

    OP_GET = 'GET'
    OP_BROADCAST = 'BROADCAST'

    @staticmethod
    def get_client_packet(packet_type, msg=None, usr=None):
        """
        Función para generar paquetes en el cliente como una nueva instancia de manera estática, esta función permite
        elegir el tipo de paquete, el mensaje y el usuario

        Parameters
        ----------
        packet_type
            Tipo de paquete
        msg
            Mensaje del paquete
        usr
            Usuario del paquete

        """
        return Packet(packet_type, None, None, msg, usr)

    @staticmethod
    def get_server_packet(packet_type, msg=None, usr=None):
        """
        Función para generar paquetes en el servidor como una nueva instancia de manera estática, esta función permite
        elegir el tipo de paquete, el mensaje y el usuario

        Parameters
        ----------
        packet_type
            Tipo de paquete
        msg
            Mensaje del paquete
        usr
            Usuario del paquete

        """
        return Packet(packet_type, None, None, msg, usr)

    def __init__(self, packet_type, src, dst, info=None, usr=None):
        self.packet_type = packet_type
        self.src = src
        self.dst = dst
        self.info = info
        self.usr = usr
        self.op = None
