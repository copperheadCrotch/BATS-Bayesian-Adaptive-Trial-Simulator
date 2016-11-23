# Cython module
import cython
cimport cython

# Import malloc, free
from libc.stdlib cimport malloc, free

# Import C function
from BATS.CriticalValueCal cimport CriticalValueCal

# Import python modules
import numpy as np
cimport numpy as np
import pandas as pd
import sys
import GammaGenerate as GammaGenerate


# Create critical value method
@cython.boundscheck(False)
@cython.wraparound(False)
@cython.cdivision(True)
cpdef OutputCriticalValue(float[:, :, ::1] gamma_vect, str pathdir, int n1, int n2, float clinSig):

    # Index
    cdef Py_ssize_t i, j, k, m
    cdef int nsim = 0
    cdef int index0 = 0, index1 = 1
    cdef dict crit_dataset = {}
    cdef float progress = float(n1 + 1) / 10
    # Critical value
    cdef float crit_arr, crit_sum
    
    clinSig = np.around(clinSig, decimals = 3)

    if n1 + n2 > 3000:
        
        nsim = 10000
    
    else:
        
        nsim = 20000
        
    if progress <= 1:
        
        progress = n1 + 1
    
    # Treatment
    sys.stdout.write("Calculate critical values...")
    for i in range(0, n1 + 1):
        

        # For status bar later
        if i % progress < 1 and i >= progress:
        
           sys.stdout.write("%d percent of values calculated..." %(i / progress * 10)) 
        
        
        # Control
        for j in xrange(0, n2 + 1):
            
            crit_sum = 0
            for k in xrange(0, nsim):
                
                crit_sum += CriticalValueCal(gamma_vect[index0, i, k], gamma_vect[index1, n1-i, k], gamma_vect[index1, j, k], gamma_vect[index0, n2-j, k], clinSig)
            
            crit_arr = crit_sum/nsim
            crit_dataset[(i, j)] = crit_arr  
            if crit_arr < 0.0001:
                
                for m in range(j + 1, n2 + 1):
                    
                    crit_dataset[(i, m)] = 0
                
                break
                    
             
    sys.stdout.write("Output critical value look up table...")
    # df = pd.DataFrame(crit_dataset.values(), index=pd.MultiIndex.from_tuples(crit_dataset.keys(), names=["Treatment", "Control"]), columns=[clinSig]).sort_index()
    df = pd.DataFrame.from_dict(crit_dataset, "index")
    df.columns = [clinSig]
    df.index = pd.MultiIndex.from_tuples(df.index)
    df.index.names = ["Treatment", "Control"]
    df = df.sort_index()
    out_file_csv = pathdir + "/CriticalValueLookUpTable%d-%d-%.3f.csv"%(n1, n2, clinSig)
    df.to_csv(out_file_csv)  # write out to a csv file 
    del crit_dataset
        
    return df


# Create critical value method
@cython.boundscheck(False)
@cython.wraparound(False)
@cython.cdivision(True)
cdef NewCriticalValue(int seed, int n1, int n2, float clinSig, str outfile):

    # Index
    cdef Py_ssize_t i, j, k, m
    cdef int nsim = 0
    cdef int index0 = 0, index1 = 1, total_index = 2
    cdef max_tps = max(n1, n2) + 1
    cdef dict crit_dataset = {}
    #     cdef float progress = float(n1 + 1) / 100
    cdef float progress = float(n1 + 1) / 10
    # Critical value
    cdef float crit_arr, crit_sum 
    
    clinSig = np.around(clinSig, decimals = 3)
    
    if n1 + n2 > 3000:
        
        nsim = 10000
    
    else:
        
        nsim = 20000
        
    if progress <= 1:
        
        progress = n1 + 1
    
    # Gamma array pointer
    cdef float *gamma_array = <float *>malloc(total_index * max_tps * nsim * sizeof(float))
    cdef float[:, :, ::1] gamma_vect = <float[:total_index, :max_tps, :nsim]> gamma_array
    
    if seed == 0:
        
        seed = np.random.randint(1, 12345, size=1)
    
    
    GammaGenerate.RVGamma(seed, max_tps, nsim, gamma_vect)
    
    # Treatment
    sys.stdout.write("Calculate critical values...")
    for i in range(0, n1 + 1):
        
        """
        if i % progress < 1 and i >= progress:
            
           sys.stdout.write("%d percent of values calculated..." %int(i / progress))
        """
     
        if i % progress < 1 and i >= progress:
        
           sys.stdout.write("%d percent of values calculated..." %(i / progress * 10)) 
             
        
        # Control
        for j in xrange(0, n2 + 1):
            
            crit_sum = 0
            for k in xrange(0, nsim):
                
                crit_sum += CriticalValueCal(gamma_vect[index0, i, k], gamma_vect[index1, n1-i, k], gamma_vect[index1, j, k], gamma_vect[index0, n2-j, k], clinSig)
            
            crit_arr = crit_sum/nsim
            crit_dataset[(i, j)] = crit_arr  
            if crit_arr < 0.0001:
                
                for m in range(j + 1, n2 + 1):
                    
                    crit_dataset[(i, m)] = 0
                
                break
                    
             
    sys.stdout.write("Output critical value look up table...")
    # df = pd.DataFrame(crit_dataset.values(), index=pd.MultiIndex.from_tuples(crit_dataset.keys(), names=["Treatment", "Control"]), columns=[clinSig]).sort_index()
    df = pd.DataFrame.from_dict(crit_dataset, "index")
    df.columns = [clinSig]
    df.index = pd.MultiIndex.from_tuples(df.index)
    df.index.names = ["Treatment", "Control"]
    df = df.sort_index()
    df.to_csv(outfile)  # write out to a csv file 
    
    free(gamma_array)
    del crit_dataset, df
        
    return 0

# Python wrapper for the function called by python side
def NewCriticalValueTable(seed, n1, n2, clinSig, outfile):
    
    import gc
    gc.collect()    
    return NewCriticalValue(seed, n1, n2, clinSig, outfile)