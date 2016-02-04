from __future__ import division
import lz4

# in bytes
_chunk_size = 2147483648

def store(data, fp):
    data = memoryview(data)
    bytes_ = data.itemsize
    max_nitems = _chunk_size / bytes_

    f = open(fp, 'w')
    f.close()

    left = 0
    while left < data.shape[0]:
        right = min(left + max_nitems, data.shape[0])

        with open(fp, 'a') as f:
            f.write(lz4.dumps(data[left:right].tobytes()))

        left = right

def load(fp):
    with open(fp, 'r') as f:
        data = f.read()

    dview = memoryview(data)
    bytes_ = data.itemsize
    max_nitems = _chunk_size / bytes_

    left = 0
    while left < dview.shape[0]:
        right = min(left + max_nitems, dview.shape[0])
        lz4.loads(dview[left:right].tobytes())
        left = right
