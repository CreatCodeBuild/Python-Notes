import json

import h2web

if __name__ == '__main__':
	app = h2web.WebServer()

	# All these context manager and functions are async, which means
	# they are not executed right away
	# but wait for inbound HTTP and executed by the server
	with app.get('name') as name:
		name.send_and_end('123')

	with app.post('user') as user:
		data = json.loads(user.data)
		# save data to somewhere
		user.send_and_end('OK')

	# besides context manger, a decorator style API is also provided
	@app.get('name')
	def get_name(connection, data):
		connection.send_and_end('123')

	@app.post('user')
	def post_user(connection, data):
		data = json.loads(connection.data)
		# save data to somewhere
		connection.send_and_end('OK')

	# A callback style is also provided
	app.get('name', get_name)
	app.post('user', post_user)

	app.run()
