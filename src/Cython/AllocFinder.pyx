import cython
cimport cython

import numpy as np
cimport numpy as np

# Function to search best patients allocation for given allocation ratio
@cython.boundscheck(False)
@cython.wraparound(False)
@cython.cdivision(True)
cpdef BestPatientAllocation(int nArm, float alloc, int nPatient):

    cdef int treatment, control, best_treatment, best_control
    
    # Truncated treatment
    treatment = np.trunc(float(nPatient) / (nArm - 1 + alloc))      
    control = nPatient - (nArm - 1) * treatment
    if abs((float(control)/treatment) - alloc) <= abs((float(control - nArm + 1)/(treatment + 1)) - alloc):
        
        best_treatment = treatment
        best_control = control        
    
    else:
        
        best_treatment = treatment + 1
        best_control = control - nArm + 1
    
    return best_treatment, best_control