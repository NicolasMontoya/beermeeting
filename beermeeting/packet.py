class Packet:

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
        return Packet(packet_type, None, None, msg, usr)

    @staticmethod
    def get_server_packet(packet_type, msg=None, usr=None):
        return Packet(packet_type, None, None, msg, usr)

    def __init__(self, packet_type, src, dst, info=None, usr=None):
        self.packet_type = packet_type
        self.src = src
        self.dst = dst
        self.info = info
        self.usr = usr
        self.op = None
