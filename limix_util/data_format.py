import re

class Chrom(object):
    def __init__(self, grp):
        super(Chrom, self).__init__()
        self._grp = grp

    @property
    def SNP(self):
        return self._grp['SNP']

    @property
    def pos(self):
        return self._grp['pos']

class GenotypeReader(object):
    def __init__(self, hdf5_fd):
        super(GenotypeReader, self).__init__()
        self._f = hdf5_fd
        self._deduce_names()

    def _deduce_names(self):
        f = self._f
        if 'genotype' in f:
            geno_grp = f['genotype']
        elif 'genotypes' in f:
            geno_grp = f['genotypes']
        else:
            raise Exception('Could not deduce the genotype'+
                            ' group.')

        self._geno_grp = geno_grp
        self._deduce_chrom_names()

    def _deduce_chrom_names(self):
        geno_grp = self._geno_grp
        names = geno_grp.keys()
        chrom_map = dict()
        for n in names:
            if 'chrom' in n:
                m = re.match(r'^chrom(\d+)$', n)
                if m is None:
                    continue
                numb = int(m.group(1))
                assert numb not in chrom_map
                chrom_map[numb] = n
        self._chrom_map = chrom_map

    @property
    def nchroms(self):
        return len(self._chrom_map)


    def chrom(self, n):
        name = self._chrom_map[n]
        return Chrom(self._geno_grp[name])
#
#
# class GenotypeSaver(object):
#     def __init__(self):
#         super(GenotypeSaver, self).__init__()
#         self.nchroms = None
#
#
#     def append(self, chrom, genotype):
#
#
#
#     def chrom(self, n):
#         name = self._chrom_map[n]
#         return self._geno_grp[name]
#
#     def SNP(self, n):
#         return self.chrom(n)['SNP']
#
#     def pos(self, n):
#         return self.chrom(n)['pos']
