from libc.stdlib cimport malloc, free
from libc.stdio cimport FILE, sprintf
from libc.string cimport strcmp
from cpython.string cimport PyString_AsString

cdef extern from "stdio.h":
    #FILE * fopen ( const char * filename, const char * mode )
    FILE *fopen(const char *, const char *)
    size_t fwrite(const void *ptr, size_t size, size_t nmemb, FILE *stream)
    #int fclose ( FILE * stream )
    int fclose(FILE *)
    #ssize_t getline(char **lineptr, size_t *n, FILE *stream);
    ssize_t getline(char **, size_t *, FILE *)

cdef char ** to_cstring_array(list_str):
    cdef char **ret = <char **>malloc(len(list_str) * sizeof(char *))
    for i in xrange(len(list_str)):
        ret[i] = PyString_AsString(list_str[i])
    return ret

#  chromosome (1-22, X, Y or 0 if unplaced)
#  rs# or snp identifier
#  Genetic distance (morgans)
#  Base-pair position (bp units)
cpdef write_map(dst_filepath, int[:] chroms, list rss,
                 int[:] gds, int[:] bps):

    cdef char **c_rss = to_cstring_array(rss)
    cdef char str_[64]
    cdef int i
    f = fopen(dst_filepath, 'w')
    for i in range(chroms.shape[0]):

        sprintf(str_, "%d", chroms[i]);
        fwrite(str_, 1, sizeof(str_), f)
        fwrite(' ', 1, sizeof(' '), f)

        fwrite(c_rss[i], 1, sizeof(c_rss[i]), f)
        fwrite(' ', 1, sizeof(' '), f)

        sprintf(str_, "%d", gds[i]);
        fwrite(str_, 1, sizeof(str_), f)
        fwrite(' ', 1, sizeof(' '), f)

        sprintf(str_, "%d", bps[i]);
        fwrite(str_, 1, sizeof(str_), f)
        fwrite('\n', 1, sizeof('\n'), f)

    # with open(dst_filepath, 'w') as f:
    #     ii = 0
    #     for (c, X) in enumerate(Xs):
    #         for i in xrange(X.shape[1]):
    #             f.write('%d %d %d %d\n' % ((c+1), ii, ii, ii))
    #             ii += 1

    fclose(f)
