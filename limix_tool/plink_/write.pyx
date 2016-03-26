from libc.stdlib cimport malloc, free
from libc.stdio cimport FILE, sprintf
from libc.string cimport strlen
# from cpython.string cimport PyString_AsString
from cpython.unicode cimport PyUnicode_AsASCIIString, PyUnicode_FromObject
from cpython.bytes cimport PyBytes_AsString
from cpython.object cimport PyObject
# from cpython.ref cimport Py_DECREF
cimport cython

cdef extern from "stdio.h":
    FILE *fopen(const char *, const char *)
    size_t fwrite(const void *ptr, size_t size, size_t nmemb, FILE *stream)
    int fclose(FILE *)
    ssize_t getline(char **, size_t *, FILE *)

# @cython.boundscheck(False)
# @cython.wraparound(False)
# @cython.initializedcheck(False)
# cdef char ** to_cstring_array(list_str):
#     cdef char **ret = <char **>malloc(len(list_str) * sizeof(char *))
#     cdef PyObject *p
#     for i in xrange(len(list_str)):
#         p = PyUnicode_AsUTF8String(list_str[i])
#         ret[i] = PyBytes_AsString(p)
#         # ret[i] = PyString_AsString(list_str[i])
#     return ret

#  chromosome (1-22, X, Y or 0 if unplaced)
#  rs# or snp identifier
#  Genetic distance (morgans)
#  Base-pair position (bp units)
@cython.boundscheck(False)
@cython.wraparound(False)
@cython.initializedcheck(False)
cpdef write_map(dst_filepath, long[:] chroms, list rss,
                 long[:] gds, long[:] bps):

    # cdef char **c_rss = to_cstring_array(rss)
    cdef char *c
    cdef char str_[64]
    cdef long i
    cdef bytes p
    f = fopen(dst_filepath, 'w')
    for i in range(chroms.shape[0]):

        p = PyUnicode_AsASCIIString(PyUnicode_FromObject(rss[i]))
        c = PyBytes_AsString(p)

        sprintf(str_, "%d", chroms[i]);
        fwrite(str_, 1, strlen(str_), f)
        fwrite(' ', 1, 1, f)

        fwrite(c, 1, strlen(c), f)
        # fwrite(c_rss[i], 1, strlen(c_rss[i]), f)
        fwrite(' ', 1, 1, f)

        sprintf(str_, "%d", gds[i]);
        fwrite(str_, 1, strlen(str_), f)
        fwrite(' ', 1, 1, f)

        sprintf(str_, "%d", bps[i]);
        fwrite(str_, 1, strlen(str_), f)
        fwrite('\n', 1, 1, f)

    fclose(f)
    # free(c_rss)

@cython.boundscheck(False)
@cython.wraparound(False)
@cython.initializedcheck(False)
cpdef write_phen_int(dst_filepath, long[:] y):

    cdef char str_[64]
    cdef long i
    f = fopen(dst_filepath, 'w')
    for i in range(y.shape[0]):
        sprintf(str_, "%d %d %d\n", i+1, i+1, y[i]);
        fwrite(str_, 1, strlen(str_), f)
    fclose(f)
