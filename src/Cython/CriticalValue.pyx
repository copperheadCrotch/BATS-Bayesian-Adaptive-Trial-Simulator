import cython
cimport cython

import numpy as np
cimport numpy as np

import pandas as pd
import sys

from libc.stdlib cimport malloc, free
from cython_gsl cimport *

DTYPE = np.float64
ctypedef np.float64_t DTYPE_t


cdef gsl_rng *r = gsl_rng_alloc(gsl_rng_mt19937)

"""
@cython.cdivision(True)
cdef float check_nodiff(float v1, float v2, float v3, float v4):
    cdef float trt, null
    trt = v1/(v1 + v2)
    null = v3/(v3 + v4)
    if trt > null:
        return 1
    return 0
"""

@cython.cdivision(True)
cpdef float check(float v1, float v2, float v3, float v4, float cval):
    cdef float trt, null
    trt = (v1/(v1 + v2)) - cval
    null = v3/(v3 + v4)
    return 1 if trt > null else 0


@cython.boundscheck(False)
@cython.wraparound(False)
@cython.cdivision(True)
cdef dict output_data(int seed, int n1, int n2, float clin_sig):

    cdef Py_ssize_t i, j, k, m, p, q, s
    cdef int nsim = 50000
    cdef int index0 = 0, index1 = 1
    cdef int maxn = max(n1, n2)+1
    cdef DTYPE_t crit_arr, crit_sum
    cdef DTYPE_t crit_sum2, crit_arr2
    # cdef np.ndarray[DTYPE_t, ndim = 1] gamma_view = np.empty(nsim)

    # check seed
    if seed != -1:
        np.random.seed(seed)
    
    # allocate memory
    sys.stdout.write("Generate Gamma random variables...")
    cdef float*** gamma_vect
    gamma_vect = <float ***> malloc(2*sizeof(float**))
    for m in range(0, 2):
        gamma_vect[m] = <float **>malloc(maxn*sizeof(float*))
        for p in range(0, maxn):
            gamma_vect[m][p] = <float *>malloc(nsim*sizeof(float))
            # gamma_view = np.random.gamma(p+1,size=nsim)
            for q in xrange(0, nsim):
                gamma_vect[m][p][q] = gsl_ran_gamma(r, p+1, 1)

    sys.stdout.write("Calculate critical values...")
    cdef dict final_data = {}
    # Equal allocation
    if clin_sig == 0 and n1 == n2:
        # Trt
        for i in range(0, n1+1):
            # Control
            for j in range(i, n2+1):
                crit_sum = 0
                for k in xrange(0, nsim):
                    crit_sum += check(gamma_vect[index0][i][k], gamma_vect[index1][n1-i][k], gamma_vect[index1][j][k], gamma_vect[index0][n2-j][k], clin_sig)
                crit_arr =  crit_sum/nsim
                final_data[(i,j)] = crit_arr
                final_data[(j,i)] = 1-crit_arr
                if crit_arr < 0.0005:
                    for s in range(j+1, n2+1):
                        final_data[(i,s)] = 0
                        final_data[(s,i)] = 1
                    break
                
    # Equal allocation            
    elif clin_sig > 0 and n1 == n2:
        # Trt
        for i in range(0, n1+1):
            # Control
            for j in range(i, n2+1):
                crit_sum = 0
                crit_sum2 = 0
                for k in xrange(0, nsim):
                    crit_sum += check(gamma_vect[index0][i][k], gamma_vect[index1][n1-i][k], gamma_vect[index1][j][k], gamma_vect[index0][n2-j][k], clin_sig)
                    crit_sum2 += check(gamma_vect[index0][j][k], gamma_vect[index1][n1-j][k], gamma_vect[index1][i][k], gamma_vect[index0][n2-i][k], clin_sig)
                crit_arr =  crit_sum/nsim
                crit_arr2 = crit_sum2/nsim
                final_data[(i,j)] = crit_arr
                final_data[(j,i)] = crit_arr2
                if crit_arr < 0.0005 and crit_arr2 > 0.9995:
                    for s in range(j+1, n2+1):
                        final_data[(i,s)] = 0
                        final_data[(s,i)] = 1
                    break

    # Assign more patients to the treatment than control, not always happen
    elif clin_sig == 0 and n1 > n2:
        # Control
        for i in range(0, n2+1):
            # Trt
            for j in range(i, n1+1):
                crit_sum = 0
                crit_sum2 = 0
                if j <= n2:
                    for k in xrange(0, nsim):
                        crit_sum += check(gamma_vect[index0][j][k], gamma_vect[index1][n1-j][k], gamma_vect[index1][i][k], gamma_vect[index0][n2-i][k], clin_sig)
                        crit_sum2 += check(gamma_vect[index0][i][k], gamma_vect[index1][n1-i][k], gamma_vect[index1][j][k], gamma_vect[index0][n2-j][k], clin_sig)
                    crit_arr =  crit_sum/nsim
                    crit_arr2 = crit_sum2/nsim
                    final_data[(j,i)] = crit_arr
                    final_data[(i,j)] = crit_arr2
                    if crit_arr > 0.9995 and crit_arr2 < 0.0005:
                        for s in range(j+1, n1+1):
                            final_data[(s,i)] = 1
                            if s <= n2:
                                final_data[(i,s)] = 0
                        break
                elif j > n2:
                    for k in xrange(0, nsim):
                        crit_sum += check(gamma_vect[index0][j][k], gamma_vect[index1][n1-j][k], gamma_vect[index1][i][k], gamma_vect[index0][n2-i][k], clin_sig)
                    crit_arr = crit_sum/nsim
                    final_data[(j,i)] = crit_arr
                    if crit_arr > 0.9995:
                        for s in range(j+1, n1+1):
                            final_data[(s,i)] = 1
                        break

    
    elif clin_sig > 0 and n1 > n2:
        # Control
        for i in range(0, n2+1):
            # Trt
            for j in range(i, n1+1):
                crit_sum = 0
                crit_sum2 = 0
                if j <= n2:
                    for k in xrange(0, nsim):
                        crit_sum += check(gamma_vect[index0][j][k], gamma_vect[index1][n1-j][k], gamma_vect[index1][i][k], gamma_vect[index0][n2-i][k], clin_sig)
                        crit_sum2 += check(gamma_vect[index0][i][k], gamma_vect[index1][n1-i][k], gamma_vect[index1][j][k], gamma_vect[index0][n2-j][k], clin_sig)
                    crit_arr =  crit_sum/nsim
                    crit_arr2 = crit_sum2/nsim
                    final_data[(j,i)] = crit_arr
                    final_data[(i,j)] = crit_arr2
                    if crit_arr > 0.9995 and crit_arr2 < 0.0005:
                        for s in range(j+1, n1+1):
                            final_data[(s,i)] = 1
                            if s <= n2:
                                final_data[(i,s)] = 0
                        break
                elif j > n2:
                    for k in xrange(0, nsim):
                        crit_sum += check(gamma_vect[index0][j][k], gamma_vect[index1][n1-j][k], gamma_vect[index1][i][k], gamma_vect[index0][n2-i][k], clin_sig)
                    crit_arr = crit_sum/nsim
                    final_data[(j,i)] = crit_arr
                    if crit_arr > 0.9995:
                        for s in range(j+1, n1+1):
                            final_data[(s,i)] = 1
                        break

    # Allocate more patients to the control than treatment. Usually use sqrt(k):1
    elif clin_sig == 0 and n1 < n2:
        # Trt
        for i in range(0, n1+1):
            # Control
            for j in range(i, n2+1):
                crit_sum = 0
                crit_sum2 = 0
                if j <= n1:
                    for k in xrange(0, nsim):
                        crit_sum += check(gamma_vect[index0][i][k], gamma_vect[index1][n1-i][k], gamma_vect[index1][j][k], gamma_vect[index0][n2-j][k], clin_sig)
                        crit_sum2 += check(gamma_vect[index0][j][k], gamma_vect[index1][n1-j][k], gamma_vect[index1][i][k], gamma_vect[index0][n2-i][k], clin_sig)
                    crit_arr =  crit_sum/nsim
                    crit_arr2 = crit_sum2/nsim
                    final_data[(i,j)] = crit_arr
                    final_data[(j,i)] = crit_arr2
                    if crit_arr < 0.0005 and crit_arr2 > 0.9995:
                        for s in range(j+1, n2+1):
                            final_data[(i,s)] = 0
                            if s <= n1:
                                final_data[(s,i)] = 1
                        break
                elif j > n1:
                    for k in xrange(0, nsim):
                        crit_sum += check(gamma_vect[index0][i][k], gamma_vect[index1][n1-i][k], gamma_vect[index1][j][k], gamma_vect[index0][n2-j][k],clin_sig)
                    crit_arr = crit_sum/nsim
                    final_data[(i,j)] = crit_arr
                    if crit_arr < 0.0005:
                        for s in range(j+1, n2+1):
                            final_data[(i,s)] = 0
                        break


    elif clin_sig > 0 and n1 < n2:
        # Trt
        for i in range(0, n1+1):
            # Control
            for j in range(i, n2+1):
                crit_sum = 0
                crit_sum2 = 0
                if j <= n1:
                    for k in xrange(0, nsim):
                        crit_sum += check(gamma_vect[index0][i][k], gamma_vect[index1][n1-i][k], gamma_vect[index1][j][k], gamma_vect[index0][n2-j][k], clin_sig)
                        crit_sum2 += check(gamma_vect[index0][j][k], gamma_vect[index1][n1-j][k], gamma_vect[index1][i][k], gamma_vect[index0][n2-i][k], clin_sig)
                    crit_arr =  crit_sum/nsim
                    crit_arr2 = crit_sum2/nsim
                    final_data[(i,j)] = crit_arr
                    final_data[(j,i)] = crit_arr2
                    if crit_arr < 0.0005 and crit_arr2 > 0.9995:
                        for s in range(j+1, n2+1):
                            final_data[(i,s)] = 0
                            if s <= n1:
                                final_data[(s,i)] = 1
                        break
                elif j > n1:
                    for k in xrange(0, nsim):
                        crit_sum += check(gamma_vect[index0][i][k], gamma_vect[index1][n1-i][k], gamma_vect[index1][j][k], gamma_vect[index0][n2-j][k], clin_sig)
                    crit_arr = crit_sum/nsim
                    final_data[(i,j)] = crit_arr
                    if crit_arr < 0.0005:
                        for s in range(j+1, n2+1):
                            final_data[(i,s)] = 0
                        break


        
    """
    # Treatment
    for i in range(0, n1+1):
      # Control
      for j in range(0, n2+1):
        crit_sum = 0
        for k in xrange(0, nsim):
          crit_sum += check(gamma_vect[index0][i][k], gamma_vect[index1][n1-i][k], gamma_vect[index1][j][k], gamma_vect[index0][n2-j][k], clin_sig)
        crit_arr =  crit_sum/nsim
        final_data[(i,j)] = crit_arr
        #final_data[(j,i)] = 1-crit_arr
        if crit_arr < 0.00001:
            for s in range(j+1, n2+1):
                final_data[(i,s)] = 0
                #final_data[(s,i)] = 1
            break
    """
    
    # free the dictionary
    # delete the gamma vector generated
    for m in range(0, 2):
        for p in range(0, maxn):
            free(gamma_vect[m][p])
        free(gamma_vect[m]) 
    free(gamma_vect)
        
    return final_data


def output(seed, n1, n2, clin_sig, out_file):
    
    df = pd.DataFrame()
    result = output_data(seed, n1, n2, clin_sig)
    sys.stdout.write("Output file...")
    df = pd.DataFrame(result.values(), index=pd.MultiIndex.from_tuples(result.keys(), names=["Treatment", "Control"]), columns=["critical"]).sort()
    file_type = out_file.rsplit(".",1)[1]
    if file_type == "csv":
        df.to_csv(out_file)  # write out to a csv file 
    elif file_type == "p":
        df.to_pickle(out_file)
    else:
        pass
    return df
