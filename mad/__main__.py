

from mad.engine import CompositeAgent
from mad.server import Server
from mad.client import Client
from mad.throttling import RandomEarlyDetection


server = Server("server", 0.1)
client = Client("client", 0.2)
client.server = server

simulation = CompositeAgent("simulation", client, server)

simulation.run_until(500)

