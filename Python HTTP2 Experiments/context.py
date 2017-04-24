def f(x):
	print('do '+x)


def get_context(x=None):
	if x is not None:
		f(x)
	else:
		return context()

class context:
	def __call__(self, *args, **kwargs):
		print('call')

	def __enter__(self):
		print('enter')
		return f

	def __exit__(self, exc_type, exc_val, exc_tb):
		print('exit')


with get_context() as c:
	c('context manager')

get_context('normal function')


