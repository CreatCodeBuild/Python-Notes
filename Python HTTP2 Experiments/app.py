import json

import h2web

if __name__ == '__main__':


	# All these context manager and functions are async, which means
	# they are not executed right away
	# but wait for inbound HTTP and executed by the server
	# with app.get('name') as name:
	# 	name.send_and_end('123')
	#
	# with app.post('user') as user:
	# 	data = json.loads(user.data)
	# 	# save data to somewhere
	# 	user.send_and_end('OK')

	# besides context manger, a decorator style API is also provided
	# @app.get('name')
	async def get_name(handler):
		print('GET name hit')
		await handler.send_and_end('GET name hit')

	# A callback style is also provided

	app = h2web.App()
	app.get('name', get_name)
	app.up()
