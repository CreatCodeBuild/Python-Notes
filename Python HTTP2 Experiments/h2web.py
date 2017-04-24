from curio import Kernel

from curio_server import h2_server


class WebServer:
	def __init__(self, public='./public'):
		self.public = public

	def run(self):
		kernel = Kernel()
		print("Try GETting:")
		print("   (Accept all the warnings)")
		kernel.run(h2_server(address=("localhost", 5000),
							 root=self.public,
							 certfile="{}.crt.pem".format("localhost"),
							 keyfile="{}.key".format("localhost")))
