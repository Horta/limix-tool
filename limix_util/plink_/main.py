from numpy import asarray
import numpy as np
from numba import jit, uint8, int64, void
from limix_util.plink_.write_map import write_map
from limix_util.plink_.write_phen import write_phen_int
from limix_util import array_
import subprocess

@jit(void(uint8[:], int64[:]), cache=True, nopython=True, nogil=True)
def _create_ped_line(line, row):
    for i in xrange(row.shape[0]):
        if row[i] == 0:
            line[4*i] = 65 # A
            line[4*i+1] = 32 # ' '
            line[4*i+2] = 65 # A
        elif row[i] == 1:
            line[4*i] = 65 # A
            line[4*i+1] = 32 # ' '
            line[4*i+2] = 66 # B
        elif row[i] == 2:
            line[4*i] = 66 # B
            line[4*i+1] = 32 # ' '
            line[4*i+2] = 66 # B

def _create_ped(dst_filepath, y, G):
    (n, p) = G.shape
    line = np.empty(p*4, dtype='uint8')
    line[:-1] = ord(' ')
    line[-1] = ord('\n')
    with open(dst_filepath, 'w') as f:
        for j in xrange(n):
            f.write('%d %d 1 1 0 %d ' % (j+1, j+1, y[j]))
            _create_ped_line(line, asarray(G[j,:], int))
            f.write(line)

def create_ped(dst_filepath, y, G):
    y = asarray(y)
    G = asarray(G)
    assert y.shape[0] == G.shape[0], 'Number of individuals mismatch.'

    u = np.unique(G)
    if not np.all([ui in set([0, 1, 2]) for ui in u]):
        raise Exception('Genetic markers matrix must contain only 0, 1, and 2.')

    u = np.unique(y)
    if not np.all([int(ui) == ui for ui in u]):
        raise Exception('This create_ped does not support non-counting'+
                        ' phenotype.')

    _create_ped(dst_filepath, y, G)

#  chromosome (1-22, X, Y or 0 if unplaced)
#  rs# or snp identifier
#  Genetic distance (morgans)
#  Base-pair position (bp units)
def create_map(dst_filepath, chroms, rss=None, gds=None, bps=None):
    chroms = asarray(chroms, int)

    if rss is None or gds is None or bps is None:
        arr = np.arange(len(chroms), dtype=int)

    if rss is None:
        rss = ['rs%d' %i for i in arr]

    if gds is None:
        gds = arr

    if bps is None:
        bps = arr

    write_map(dst_filepath, chroms, rss, gds, bps)

def create_phen(filepath, y):
    y = asarray(y)
    if array_.isint_alike(y):
        write_phen_int(filepath, asarray(y, int))
    else:
        raise NotImplementedError('create_phen is not suitable for non-int'+
                                  ' phenotype yet.')

def create_bed(filepath, na_rep='-9', cod_type='binary'):
    cmd = ["plink", "--file", filepath, "--out", filepath, "--make-bed",
          "--noweb", '--missing-phenotype', na_rep]
    if cod_type == 'binary':
        cmd.append('--1')
    subprocess.call(cmd)


if __name__ == '__main__':
    dst_filepath = '/Users/horta/out.ped'
    random = np.random.RandomState(539)
    G = random.randint(0, 3, (4, 10))
    y = random.randint(0, 2, 4)
    create_ped(dst_filepath, y, G)
    create_map('/Users/horta/out.map', np.ones(30))
