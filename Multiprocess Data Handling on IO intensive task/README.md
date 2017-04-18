This note demonstrates how to use __multiple processes on data parallelism tasks__.

The experiment is only suitable for GB level data. In my case, I used 12 GB of data.

You need to create a `data/` dir to run this experiment.

Under `data/`, you need to create `raw/` and `processed/` dirs.

See the notebook for details.

### Please read the notebook first

### Multi-process code

Now, we are pretty confident that our single version is fast enough. Let's summon the multi-process demon.

We use the `multiprocessing.Pool` class. This class has a `map` function which allows you to do data parallelism like it's nothing.

`map` function blocks until all results are computed. You don't need to worry about spawning, passing data, listening and joining processes at all. You just write your code as if it's single processed.

This function is useful when your data are indenpendent from one anathor. In our case, each file can be handled individually, so that each process only has to be responsible for itself.

[multiprocessing](https://docs.python.org/3.5/library/multiprocessing.html) module API here.

[Pool](https://docs.python.org/3.5/library/multiprocessing.html#multiprocessing.pool.Pool) API here.

Our code goes like:
```python
def f(path):
	view = bird_view_map(read_velodyne_data(path[0]))
	cv2.imwrite(''.join([path[1], '/', os.path.basename(path[0])[:-4], '.png']), view)

def generate_birdviews(data_paths, to_dir, workers):
	"""
	This function process velodyne data to birdview in parallel
	:param data_paths: a list of paths to velodyne xxx.bin files
	:param     to_dir: write birdview maps to this directory
	:param    workers: number of processes
	"""
	with Pool(workers) as p:
		to_dirs = [to_dir] * len(data_paths)
		p.map(f, list(zip(data_paths, to_dirs)))


if __name__ == '__main__':
	t = time.time()
	generate_birdviews(glob('data/raw/*.bin')[:100], to_dir='data/processed', workers=8)
	used = time.time() - t
	print('Simple multi-processed version:', used, 'seconds')
```
Notice 2 things:
1. In `Pool.map(func, iterable)`, `func` must be defined at the module level. In other words, it has to be a global function.
2. You have to call `.map` under `__main__` namespace. Or you will have a major problem. You can do some research to know why.

The result on my i7 (4 cores, 8 hyperthreads)
```
Simple multi-processed version: 37.5 seconds
```

As you can see, we push down the time to less than 1/3. 

Why isn't it 1/8 ? First, it's hyper threadings, it's not real 8 cores. Second, inter process communication has overhead.

But still, with mere 10 lines of code, we boost the performance 250%. This is incredible gain.

However, we can still optimize further. Remember, interprocess communication is heavy. Even spawning a new process introduce a lot of overhead.

Do you know how many processes our code spawns? 100 processes!

Wait, isn't it 8? Yes, only 8 processes are alive at a time. But, since the list has 100 elements, there are 100 process ever alive in total. That's a huge waste since each process only process 1 file!

It would be wise if we divide our data into 8 pieces instead of 100 pieces and let only 8 processes to deal with them.

Let's modifly the code:
```Python
def f2(paths):
	paths =  pickle.loads(paths)
	_from, to = paths
	for i in range(len(to)):
		view = bird_view_map(read_velodyne_data(_from[i]))
		cv2.imwrite(''.join([to[i], '/', os.path.basename(_from[i])[:-4], '.png']), view)


def generate_birdviews_2(data_paths, to_dir, workers):
	"""
	This function process velodyne data to birdview in parallel
	:param data_paths: a list of paths to velodyne xxx.bin files
	:param     to_dir: write birdview maps to this directory
	:param    workers: number of processes
	"""
	with Pool(workers) as p:
		to_dirs = [to_dir] * len(data_paths)
		n = np.int(np.ceil(len(data_paths)/workers))
		_list = [pickle.dumps((data_paths[i:i+n], to_dirs[i:i+n])) for i in range(0, len(data_paths), n)] 
		p.map(f2, _list)
        
if __name__ == '__main__':
	t = time.time()
	generate_birdviews_2(glob('data/raw/*.bin')[:100], to_dir='data/processed', workers=8)
	used2 = time.time() - t
	print('Better multi-processed version:', used2, 'seconds')
```
As you can see, we divide the data into 8 pieces by
```
_list = [pickle.dumps((data_paths[i:i+n], to_dirs[i:i+n])) for i in range(0, len(data_paths), n)] 
```
Notice that we use `pickle` to serialize our data, since Python uses the unix tradition that processes communicate through streams/files. Therefore, we can only pass `bytes`, `string` or `int` to another process. (I am not sure if you can pass float). Here we serialize a Python object to Python `bytes`.

The result is:
```
Better multi-processed version: 36.4 seconds
```
A 3% gain. Yeah!

### Conclusion
Through 2 steps of optimization, with less than 10 lines of code, we obtain an overall 293% performance gain. Remember, Python is slow, but, it's not hard to make it less slow.

You might want to ask, why bother? If my Python code is slow, I can always write the slow part with C++.

I have 2 arguments to justify it:
1. We, Python programmers say that we will rewrite slow code with C/C++. Nobody does it. It is not that easy to write a native extension for Python. Sometimes it's just not worth it to write a native code for some one-time use code. If you are writing a more general utility that will be used by many developers, then it's worth it. Numpy etc. We are not doing extreme optimization here.
2. No matter how fast your single thread code is, you still need to write milti-process parallel code someitmes. This experiment use Python as an example, but the principle applies to all languages. If you have data parallelism, consider multi-process.

Ok, hope this is helpful to you.

Best
