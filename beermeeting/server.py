from socketserver import ThreadingMixIn, TCPServer
from beermetting.database import Database


class BeerServer(ThreadingMixIn, TCPServer):

    def __init__(self, server_address, RequestHandlerClass, config, bind_and_activate=True):
        super().__init__(server_address, RequestHandlerClass, bind_and_activate)
        Database.get_instance(config.username, config.password, config.dsn)
