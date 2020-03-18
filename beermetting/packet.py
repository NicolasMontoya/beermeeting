class Packet:

    SERVER_REGISTER = 1
    SEND_DATA = 2

    @staticmethod
    def get_client_packet(msg: str):
        packet_ob = msg.split('|')
        if len(packet_ob) > 1:
            return Packet(1, None, None)

    @staticmethod
    def get_server_packet(msg=None, usr=None):
        return Packet(1, None, None, msg, usr)

    def __init__(self, packet_type, src, dst, info='', usr=None):
        self.packet_type = packet_type
        self.src = src
        self.dst = dst
        self.info = info
        self.usr = usr
