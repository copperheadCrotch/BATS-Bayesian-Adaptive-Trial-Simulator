# Import cython
import cython
cimport cython

from cython_gsl cimport *

# Import malloc, free
from libc.stdlib cimport malloc, free

import sys
import numpy as np
cimport numpy as np

DTYPE = np.float64
ctypedef np.float64_t DTYPE_t


# Function to calculate posterior probability
@cython.boundscheck(False)
@cython.wraparound(False)
@cython.cdivision(True)
cdef PosteriorProbability(int nsTrt, int nfTrt, int nsControl, int nfControl, int prioraTrt,
                          int priorbTrt, int prioraControl, int priorbControl, float clinSig,
                          int seed):


    cdef Py_ssize_t i, j
    cdef int beta_nsim = 50000
    cdef float a, b, posteriorprob
    cdef float* posterior_pointer = <float *>malloc(beta_nsim * sizeof(float))
    cdef float [::1] posterior = <float [:beta_nsim]> posterior_pointer
    cdef gsl_rng *beta_r = gsl_rng_alloc(gsl_rng_mt19937) 

    # Set seed
    gsl_rng_set(beta_r, seed) 
    sys.stdout.write("Calculating posterior probability...")

    for i in range(0, beta_nsim):
        
        a = gsl_ran_beta(beta_r, nsTrt, nfTrt)
        b = gsl_ran_beta(beta_r, nsControl, nfControl)
        if a > b:
            
            posterior[i] = 1
            
        else: 
            
            posterior[i] = 0
                
    posteriorprob = np.mean(np.array(posterior))      
    sys.stdout.write("The probability is %.3f"%posteriorprob)
                
    gsl_rng_free(beta_r)
    free(posterior_pointer)
    return 0


# For GUI
def CalPosteriorProbability(nTrt = [0, 0], nControl = [0, 0], priorTrt = [0, 0], 
                            priorControl = [0, 0], clinSig = 0, seed = 12345):

    # Set values
    nsTrt = nTrt[0]
    nfTrt = nTrt[1]
    nsControl = nControl[0]
    nfControl = nControl[1]
    prioraTrt = priorTrt[0]
    priorbTrt = priorTrt[1]     
    prioraControl = priorControl[0]
    priorbControl = priorControl[1]       
    # Run the calculation of posterior probability in BATS
    finish_flag = 0       
    finish_flag = PosteriorProbability(nsTrt, nfTrt, nsControl, nfControl, prioraTrt, 
                                          priorbTrt, prioraControl, priorbControl, clinSig,
                                          seed)
    
    # Import gc to collect garbage
    import gc
    gc.collect()
    
    # Return the flag to GUI
    return finish_flag
    
    
    
