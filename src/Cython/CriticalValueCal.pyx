import cython
cimport cython


# Function to calculate the critical value
@cython.boundscheck(False)
@cython.wraparound(False)
@cython.cdivision(True)
cdef float CriticalValueCal(float v1, float v2, float v3, float v4, float clinSig):
    
    # trt: treatment, gamma variable v1, v2
    # null: control, gamma variable v3, v4
    cdef float treatment_effect, control_effect
    
    treatment_effect = v1/(v1 + v2) - clinSig
    control_effect = v3/(v3 + v4)
    return 1 if treatment_effect > control_effect else 0