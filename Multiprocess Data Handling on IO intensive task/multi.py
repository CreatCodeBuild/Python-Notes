from multiprocessing import Pool
from glob import glob
import cv2
import os
import numpy as np
from io import BufferedReader
import time
import pickle


"""
First, let's define helper functions.
We use the faster version of read_velodyne_data here.
"""
def read_velodyne_data(file_path):
	"""
	Read velodyne binary data and return a numpy array
	"""

	# First, check the size of this file to see if it's a valid velodyne binary file
	size = os.stat(file_path).st_size
	if size % 16 != 0:
		raise Exception('The size of '+file_path+' is not dividible by 16 bytes')

	with open(file_path, 'rb') as f:
		# Allocate memory for numpy array
		velodyne_data = np.empty(shape=(size//16, 4), dtype=np.float32)
		
		# Read the data, 16 bytes each time
		i = 0
		reader = BufferedReader(f)
		read_bytes = reader.read(16)
		while read_bytes:
			velodyne_data[i] = np.frombuffer(read_bytes, dtype=np.float32)
			read_bytes = reader.read(16)
			i += 1
		
		# Check whether correct amount of bytes were read
		if i != size/16:
			error = ' '.join(['The file size is', str(size), ', but', str(i), 'bytes were read'])
			raise Exception(error)

		return velodyne_data


def bird_view_map(velodyne_data):
	"""
	Implements the method in https://arxiv.org/pdf/1611.07759.pdf
	:param velodyne_data: a list of velodyne cloud points
	:return: 2D image with 3 channels: height, intensity and density
	"""
	bird_view = np.zeros(shape=(1600, 1600, 3), dtype=np.float32)
	for point in velodyne_data:
		x = point[0]
		y = point[1]
		z = point[2]
		r = point[3]
		# if (-40 <= x <= 40) and (-40 <= y <= 40):
		xi = 800 - np.int(np.ceil(x/0.1))
		yi = 800 - np.int(np.ceil(y/0.1))
		if -z > bird_view[yi][xi][0]:
			bird_view[yi][xi][0] = -z
			bird_view[yi][xi][1] = r
			bird_view[yi][xi][2] += 1

	# todo: normalize birdview with the real method
	bird_view[:,:,0] = np.interp(bird_view[:,:,0], xp=(np.min(bird_view[:,:,0]), np.max(bird_view[:,:,0])), fp=(0, 255))
	bird_view[:,:,1] = np.interp(bird_view[:,:,1], xp=(0, 1), fp=(0, 255))
	bird_view[:,:,2] = np.interp(bird_view[:,:,2], xp=(np.min(bird_view[:,:,2]), np.max(bird_view[:,:,2])), fp=(0, 255))
	return bird_view



"""
Now, let's define the multi-process code.
We use the multiprocessing.Pool class. This class has a map function which allows you to do data parallelism like it's nothing.

With map function, you don't need to worry about spawning, passing data, listening and joining processes at all.
You just write your code as if it's single processed.

This function is useful when your data are indenpendent from one anathor. 
In our case, each file can be handled individually, so that each process only has to be responsible for itself.
"""
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



"""
Can we optimize further?
"""
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
	print(used2)
