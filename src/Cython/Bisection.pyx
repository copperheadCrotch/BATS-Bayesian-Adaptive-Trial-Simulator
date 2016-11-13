import cython
cimport cython

# Import C function
from CriticalValueCal cimport CriticalValueCal

import numpy as np
cimport numpy as np
import sys

# Bisection search method
@cython.boundscheck(False)
@cython.wraparound(False)
@cython.cdivision(True)
cdef OutputBisection(float[:, :, ::1] gamma_vect, int nsim, int n1, int n2, float clinSig, float predSuccess, int [::1] crit_array):

    # Index
    cdef Py_ssize_t i, j, k
    cdef int bisect_nsim = 500
    cdef int index0 = 0, index1 = 1
    cdef int bisect_stop = 1, mid_n, min_n, max_n, o_n
    # Critical value
    cdef float crit_arr, crit_sum

    # Assume allocation between treatment is equal
    # N1 Treatment
    # N2 Control
    sys.stdout.write("Calculate critical values...")
    for i in xrange(0, n1 + 1):
        # Initialize for the bisection search
        # To find the value meet the successful boundary
        sys.stdout.write("Calculate for %d" %i)
        max_n = n2
        min_n = 0
        # Get the integer
        mid_n = np.rint(max_n/2)
        while max_n > min_n:
             
            crit_sum = 0
            # Quick search
            for k in range(0, bisect_nsim):
            
                crit_sum += CriticalValueCal(gamma_vect[index0, i, k], gamma_vect[index1, n1-i, k], gamma_vect[index1, mid_n, k], gamma_vect[index0, n2-mid_n, k], clinSig)
            
            crit_arr = crit_sum/bisect_nsim
            
            # Bisection search
            if crit_arr < predSuccess:
            
                max_n = mid_n - 1
                mid_n = np.rint((max_n + min_n)/2)
            
            elif crit_arr > predSuccess:
            
                min_n = mid_n + 1
                mid_n = np.rint((min_n + max_n)/2)
            
            elif crit_arr == predSuccess:
            
                min_n = mid_n
        
        sys.stdout.write("Done for %d" %i)        
        # Exact verification
        while bisect_stop:
            
            crit_sum = 0
            for k in xrange(0, nsim):
            
                crit_sum += CriticalValueCal(gamma_vect[index0, i, k], gamma_vect[index1, n1-i, k], gamma_vect[index1, min_n, k], gamma_vect[index0, n2-min_n, k], clinSig)
            
            crit_arr = crit_sum/nsim
            
            if crit_arr > predSuccess:
            
                if o_n == -1:
                
                    bisect_stop = 0
                
                else:
                
                    min_n = min_n + 1
                    o_n = 1
                    
            elif crit_arr < predSuccess:
                
                if o_n == 1:
                
                    min_n = min_n - 1
                    bisect_stop = 0
                
                else:
                
                    min_n = min_n - 1
                    o_n = -1
                    
            elif crit_arr == predSuccess:
               
                min_n = min_n + 1
                bisect_stop == 0
        
        crit_array[i] = min_n
    
    return    
        
def Bisection(gamma_vect, nsim, n1, n2, clinSig, predSuccess, crit_array):
    
    return OutputBisection(gamma_vect, nsim, n1, n2, clinSig, predSuccess, crit_array)
