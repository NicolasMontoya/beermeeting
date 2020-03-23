from beermeeting.server import BeerServer
from beermeeting.request import EchoRequestHandler
import config
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(name)s: %(message)s',
                    )

if __name__ == '__main__':
    address = ('localhost', 9999)  # let the kernel assign a port
    server = BeerServer(address, EchoRequestHandler, config)
    server.serve_forever()
