from curio import Kernel

from curio_server import h2_server, H2Server


class App:
	def __init__(self, port=5000, root='./public'):
		self.port = port
		self.root = root
		self.server = None
		self.routes = {'GET': {}, 'POST': {}}

	def up(self):
		kernel = Kernel()
		print("Try GETting:")
		print("   (Accept all the warnings)")
		kernel.run(h2_server(address=("localhost", self.port),
							 root=self.root,
							 certfile="{}.crt.pem".format("localhost"),
							 keyfile="{}.key".format("localhost"),
							 app=self))

	def register_route(self, method: str, route: str, handler):
		assert method in ['GET', 'POST']
		self.routes[method][route] = handler

	def get(self, route: str, handler=None):
		self.register_route('GET', route, handler)
