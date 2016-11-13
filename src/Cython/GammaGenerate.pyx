import cython
cimport cython

from cython_gsl cimport *

import sys

# Function to generate gamma random variable
@cython.boundscheck(False)
@cython.wraparound(False)
@cython.cdivision(True)
cdef RandomVaribleGamma(int seed, int max_tps, int gamma_nsim,  float [:, :, ::1] gamma_vect):

    cdef Py_ssize_t m, p, q
    cdef int total_index = 2
    cdef gsl_rng *gamma_r = gsl_rng_alloc(gsl_rng_mt19937) 
    cdef float progress = float(max_tps * total_index) / 10
    
    # Set seed
    gsl_rng_set(gamma_r, seed) 
    # Generate gamma random variables 
    # Set seed for gamma random variable generation 
    sys.stdout.write("Generating gamma random variables...")
        
    for m in range(0, total_index):
        
        for p in range(0, max_tps):
        
            if p % progress < 1 and p >= progress:
            
                sys.stdout.write("%d percent of values calculated..." %((p + max_tps * m)/ progress * 10))
            
            for q in xrange(0, gamma_nsim):
            
                gamma_vect[m, p, q] = gsl_ran_gamma(gamma_r, p + 1, 1)
    
    gsl_rng_free(gamma_r)
    
    return


def RVGamma(seed, max_tps, gamma_nsim, gamma_vect):
    
    RandomVaribleGamma(seed, max_tps, gamma_nsim, gamma_vect)