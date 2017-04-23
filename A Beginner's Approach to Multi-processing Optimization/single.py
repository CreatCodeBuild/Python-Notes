@profile
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
        while reader.peek(16):
            read_bytes = reader.read(16)
            velodyne_data[i] = np.frombuffer(read_bytes, dtype=np.float32)
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


# You might wonder why I import stuff here. I know it's not a good practice. But it's just a demo
# If you wonder why it's still valid Python code, take a look at how Python evaluate code
from glob import glob
import cv2
import os
import numpy as np
from io import BufferedReader
import time


paths = glob('data/raw/*.bin')[:10]
t = time.time()
for path in paths:
    data = read_velodyne_data(path)
    view = bird_view_map(data)
    cv2.imwrite(''.join(['data/processed/', os.path.basename(path)[:-4], '.png']), view)
used = time.time() - t
print('Single processed version used', used, 'seconds to process', len(paths), 'files')
