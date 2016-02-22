from libc.stdlib cimport malloc, free
from libc.stdio cimport FILE, sprintf
from libc.string cimport strcmp, strlen
from cpython.string cimport PyString_AsString
cimport cython

cdef extern from "stdio.h":
    FILE *fopen(const char *, const char *)
    size_t fwrite(const void *ptr, size_t size, size_t nmemb, FILE *stream)
    int fclose(FILE *)

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
