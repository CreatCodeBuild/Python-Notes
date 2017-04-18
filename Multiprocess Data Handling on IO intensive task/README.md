This note demonstrates how to use __multiple processes on data parallelism tasks__.

The experiment is only suitable for GB level data. In my case, I used 12 GB of data.

You need to create a `data/` dir to run this experiment.

Under `data/`, you need to create `raw/` and `processed/` dirs.

See the notebook for details.

### Please read the notebook first

### Multi-process code

Now, we are pretty confident that our single version is fast enough. Let's summon the multi-process demon.

We use the `multiprocessing.Pool` class. This class has a `map` function which allows you to do data parallelism like it's nothing.

With `map` function, you don't need to worry about spawning, passing data, listening and joining processes at all. You just write your code as if it's single processed.

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

