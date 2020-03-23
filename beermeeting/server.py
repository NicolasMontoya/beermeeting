from socketserver import ThreadingMixIn, TCPServer
from beermeeting.database import Database


class BeerServer(ThreadingMixIn, TCPServer):
    """
    Servidor principal, este servidor funciona mediante multiples hilos y permite la gestión de diferentes clientes
    al mismo tiempo. Este servidor también contiene una instancia de base de datos configurada para gestionar los
    usuarios del sistema.

    El servidor usa el driver CX_ORACLE para conectarse al esquema beermeeting y gestionar los usuarios que ingresan
    al sistema.

    En el archivo beermeeting.sql se tiene el esquema necesario para que el proyecto funcione de manera local.

    """

    def __init__(self, server_address, RequestHandlerClass, config, bind_and_activate=True):
        super().__init__(server_address, RequestHandlerClass, bind_and_activate)
        Database.get_instance(config.username, config.password, config.dsn)
