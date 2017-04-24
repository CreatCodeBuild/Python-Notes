from h2web import app

if __name__ == '__main__':

	# A basic callback style API is provided
	async def get_name(handler):
		print('GET name hit')
		await handler.send_and_end('GET name hit')

	app = app.App()
	app.get('name', get_name)
	app.up()
