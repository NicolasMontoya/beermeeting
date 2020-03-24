import unittest
from beermeeting.client import Client
from beermeeting.user import User
from beermeeting.packet import Packet


class TestClient(unittest.TestCase):

    def test_register(self):
        client = Client()
        usr = User("127.0.0.1", 'NIET', 20, 'NICOLAS', 'LN', 'M', 29000)
        new_client = Packet(Packet.SERVER_REGISTER, None, None, '', usr)
        message = client.process_packet(new_client)
        self.assertTrue(message, f"Ingreso con {client.user.username}")

    def test_op_get(self):
        client = Client()
        usr = User("127.0.0.1", 'NIET', 20, 'NICOLAS', 'LN', 'M', 29000)
        new_client = Packet(Packet.SERVER_OPERATION, None, None, [usr], usr)
        new_client.op = Packet.OP_GET
        message = client.process_packet(new_client)
        self.assertTrue(len(message), 1)

    def test_op_res(self):
        client = Client()
        usr = User("127.0.0.1", 'NIET', 20, 'NICOLAS', 'LN', 'M', 29000)
        packet = Packet(Packet.SERVER_RESPONSE, None, None, "HI BUDDY", usr)
        packet.op = Packet.OP_GET
        message = client.process_packet(packet)
        self.assertTrue(message, "HI BUDDY")

    def test_op_error(self):
        client = Client()
        usr = User("127.0.0.1", 'NIET', 20, 'NICOLAS', 'LN', 'M', 29000)
        with self.assertRaises(Exception):
            packet = Packet(Packet.SERVER_ERROR, None, None, "HI BUDDY", usr)
            client.process_packet(packet)


if __name__ == '__main__':
    unittest.main()
