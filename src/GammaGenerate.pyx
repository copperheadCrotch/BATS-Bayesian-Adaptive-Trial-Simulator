# cython module to generate large C-type arrays
import cython
cimport cython

import numpy as np
cimport numpy as np

from libc.stdlib cimport malloc, free

DTYPE = np.float64
ctypedef np.float64_t DTYPE_t

@cython.boundscheck(False)
@cython.wraparound(False)
@cython.cdivision(True)
cdef dict generate_gamma_table(int n):

    cdef Py_ssize_t m, p, q
    cdef int nsim = 50000
    cdef np.ndarray[DTYPE_t, ndim = 1] gamma_view = np.empty(nsim)
	
    cdef float*** gamma_vect
    gamma_vect = <float ***> malloc(2*sizeof(float**))
    for m in range(0, 2):
        gamma_vect[m] = <float **>malloc(n*sizeof(float*))
        for p in range(0, n):
            gamma_vect[m][p] = <float *>malloc(nsim*sizeof(float))
            gamma_view = np.random.gamma(p+1,size=nsim)
            for q in xrange(0, nsim):
                gamma_vect[m][p][q] = gamma_view[q]
				
