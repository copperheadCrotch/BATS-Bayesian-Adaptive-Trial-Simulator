import cython
cimport cython

from cython_gsl cimport *
from libc.stdlib cimport malloc, free

# Import C function
from CriticalValueCal cimport CriticalValueCal

import numpy as np
cimport numpy as np
import pandas as pd
import sys
import os
import random
import matplotlib.pyplot as plt
# import CreateCriticalValueTable as CreateCriticalValueTable


DTYPE = np.float64
ctypedef np.float64_t DTYPE_t


# Bisection search method
@cython.boundscheck(False)
@cython.wraparound(False)
@cython.cdivision(True)
cdef Bisection(float[:, :, ::1] gamma_vect, int nsim, int nArm, int [:, ::1] prior, int n1, int n2, float predSuccess, float clinSig, int [:, ::1] critical_array):

    # Index
    cdef Py_ssize_t i, j, k
    cdef int bisect_nsim = 500
    cdef int index0 = 0, index1 = 1
    cdef int bisect_stop = 1, mid_n, min_n = 0, max_n, o_n = 0
    # Critical value
    cdef float crit_arr, crit_sum = 0

    # Assume allocation between treatment is equal
    # N1 Treatment
    # N2 Control
    sys.stdout.write("Calculate posterior probability...")
    for j in range(0, nArm - 1):
        
        for i in xrange(0, n1 + 1):
            
            # Initialize for the bisection search
            # To find the value meet the successful boundary
            max_n = n2
            min_n = 0
            # Get the integer
            mid_n = np.rint(max_n / 2)
            while max_n > min_n:
                 
                crit_sum = 0.0
                # Quick search
                for k in range(0, bisect_nsim):
                    
                    crit_sum += CriticalValueCal(gamma_vect[index0, i + prior[j, 0] - 1, k], gamma_vect[index1, n1 + prior[j, 1] - 1 - i, k], gamma_vect[index1, mid_n + prior[(nArm - 1), 0] - 1, k], gamma_vect[index0, n2 - mid_n + prior[(nArm - 1), 1] - 1, k], clinSig)
                
                crit_arr = crit_sum / bisect_nsim
                # Bisection search
                if crit_arr < predSuccess:
                
                    max_n = mid_n - 1
                    mid_n = np.rint((max_n + min_n) / 2)
                
                elif crit_arr > predSuccess:
                
                    min_n = mid_n + 1
                    mid_n = np.rint((min_n + max_n) / 2)
                
                elif crit_arr == predSuccess:
                
                    min_n = mid_n
                    max_n = min_n
            
            bisect_stop = 1
            # Exact verification
            while bisect_stop and min_n > 0:
                
                crit_sum = 0
                for k in xrange(0, nsim):
                
                    crit_sum += CriticalValueCal(gamma_vect[index0, i + prior[j, 0] - 1, k], gamma_vect[index1, n1 + prior[j, 1] - 1 - i, k], gamma_vect[index1, min_n + prior[(nArm - 1), 0] - 1, k], gamma_vect[index0, n2 - min_n + prior[(nArm - 1), 1] - 1, k], clinSig)
                
                crit_arr = crit_sum / nsim
                if crit_arr > predSuccess:
                
                    if o_n == -1:
                    
                        bisect_stop = 0
                    
                    else:
                    
                        min_n = min_n + 1
                        o_n = 1
                        
                elif crit_arr < predSuccess:
                    
                    if min_n == 0:
                        
                        bisect_stop = 0
                    
                    elif o_n == 1:
                    
                        min_n = min_n - 1
                        bisect_stop = 0
                    
                    else:
                    
                        min_n = min_n - 1
                        o_n = -1
                        
                elif crit_arr == predSuccess:
                   
                    min_n = min_n + 1
                    bisect_stop = 0

            critical_array[j, i] = min_n


# For predictive probability
@cython.boundscheck(False)
@cython.wraparound(False)
@cython.cdivision(True)
cdef CalInterimPredictiveProbability(int nsim, int nArm, int nStage, int [:, ::1] prior, 
                          float predSuccess, float predClinSig, int [::1] treatment_add, int control_add, 
                          int [:, :, ::1] sim_dataset, int [:, ::1] tps_array, int gamma_nsim, float [:, :, ::1] gamma_vect, 
                          float [:, :, ::1] interim_crit, str pathdir, list effColHeader, list patColHeader):
    
    cdef Py_ssize_t ci, cj, ck, cl, cm, cn, cp, co, cq, cs
    cdef int beta_index1, beta_index2, beta_index3, beta_index4
    # Obs_succ_control, trt: observed data
    # Pred_trt_add, control_add: patients added
    # Pred_trt, pred_control: pred_data + observed_data
    cdef int obs_succ_control, obs_succ_treatment, predict_nSuccess
    # New patients added
    # Total patients 
    cdef int predict_treatment, predict_control
    predict_treatment_max = max(treatment_add[0:(nArm - 1)]) + max(tps_array[0:(nArm - 1), nStage])
    predict_control = control_add + tps_array[nArm - 1, nStage]    
    cdef int index_treatment, index_control, cl_copy, cm_copy, cq_copy
    cdef float cpower_sum
    # Total index
    cdef dict pred_control_dict = {}
    cdef dict pred_treatment_dict = {}
    cdef dict pred_total_dict = {}
    # Critical value for bisection search methods
    cdef int *critical_array_pointer = <int *>malloc((nArm - 1) * (predict_treatment_max + 1) * sizeof(int))
    cdef int [:, ::1] critical_array = <int[:(nArm - 1), :(predict_treatment_max + 1)]> critical_array_pointer

    cdef float *probBetaBinomial_treatment_pointer = <float *>malloc((nArm - 1) * (max(treatment_add) + 1) * nsim * sizeof(float))
    cdef float [:, :, ::1] probBetaBinomial_treatment = <float[:(nArm - 1), :(max(treatment_add) + 1), :nsim]> probBetaBinomial_treatment_pointer
    # Control
    cdef float *probBetaBinomial_control_pointer = <float *>malloc((control_add + 1) * nsim * sizeof(float))
    cdef float [:, ::1] probBetaBinomial_control = <float[:(control_add + 1), :nsim]> probBetaBinomial_control_pointer
    
    # Use bisection to find the maximum possible number of patients for control arm
    Bisection(gamma_vect, gamma_nsim, nArm, prior, predict_treatment_max, predict_control, predSuccess, predClinSig, critical_array)                

    sys.stdout.write("Calculate beta-binomial probabilities for control at stage %d..."%(nStage + 1))
    # Calculate posterior predictive probability            
    # Write out the critical array file     
    # Control arm
    for cl in xrange(0, control_add + 1):
        
        for ck in xrange(0, nsim):
            
            # Observed success in the control at the final stage of Phase II
            obs_succ_control = sim_dataset[nArm - 1, nStage, ck]
                
            if obs_succ_control in pred_control_dict:
                
                cl_copy = pred_control_dict[obs_succ_control]
                probBetaBinomial_control[cl, ck] = probBetaBinomial_control[cl, cl_copy]
                
            else:
                
                # Create element for choose function
                predict_nSuccess = cl + obs_succ_control 
                beta_index1 = predict_nSuccess + prior[(nArm - 1), 0] - 1
                beta_index2 = cl
                beta_index3 = tps_array[nArm - 1, nStage] + control_add - predict_nSuccess + prior[(nArm - 1), 1] - 1
                beta_index4 = control_add - cl
                # Calculate beta binomial probability
                probBetaBinomial_control[cl, ck] =  gsl_sf_choose(beta_index1, beta_index2) * gsl_sf_choose(beta_index3, beta_index4)/gsl_sf_choose(predict_control + np.sum(prior[(nArm - 1), :]) - 1, control_add)
                pred_control_dict[obs_succ_control] = ck
           
        pred_control_dict.clear()
        
    del pred_control_dict   
    
    sys.stdout.write("Calculate beta-binomial probabilities for treatment at stage %d..."%(nStage + 1))                
    # Treatment arm
    for ci in range(0, nArm - 1):
        
        predict_treatment = treatment_add[ci] + tps_array[ci, nStage]    
        for cj in xrange(0, nsim):
            
            obs_succ_treatment = sim_dataset[ci, nStage, cj]
            obs_succ_control = sim_dataset[nArm - 1, nStage, cj]
                
            if obs_succ_treatment in pred_treatment_dict:
                
                cm_copy = pred_treatment_dict[obs_succ_treatment]
                    
                for cp in xrange(0, treatment_add[ci] + 1):
                        
                    probBetaBinomial_treatment[ci, cp, cj] = probBetaBinomial_treatment[ci, cp, cm_copy]
                    
            else:
                # Simulated success for the added patients
                for cm in xrange(0, treatment_add[ci] + 1):
                
                    predict_nSuccess = cm + obs_succ_treatment
                    beta_index1 = predict_nSuccess + prior[ci, 0] - 1
                    beta_index2 = cm
                    beta_index3 = tps_array[ci, nStage] + treatment_add[ci] - predict_nSuccess + prior[ci, 1] - 1
                    beta_index4 = treatment_add[ci] - cm
                    # Calculate beta binomial probability
                    probBetaBinomial_treatment[ci, cm, cj] =  gsl_sf_choose(beta_index1, beta_index2) * gsl_sf_choose(beta_index3, beta_index4)/gsl_sf_choose(predict_treatment + np.sum(prior[ci, :]) - 1 , treatment_add[ci])
                                            
                pred_treatment_dict[obs_succ_treatment] = cj
 
            if (obs_succ_control, obs_succ_treatment, treatment_add[ci]) in pred_total_dict:
                
                interim_crit[ci, nStage, cj] = pred_total_dict[(obs_succ_control, obs_succ_treatment, treatment_add[ci])]
                
            else:
                        
                cpower_sum = 0

                for cq in xrange(0, treatment_add[ci] + 1):                      
                          
                    index_treatment = cq + obs_succ_treatment 
                    cq_copy = critical_array[ci, index_treatment] - obs_succ_control
                            
                    if cq_copy < 0:
                            
                        cq_copy = 0
                            
                    elif cq_copy > control_add:
                            
                        cq_copy = control_add + 1
                            
                    for cl in xrange(0, cq_copy):
                            
                        cpower_sum += probBetaBinomial_control[cl, cj] * probBetaBinomial_treatment[ci, cq, cj]
                            
                interim_crit[ci, nStage, cj] = cpower_sum     
                pred_total_dict[(obs_succ_control, obs_succ_treatment, treatment_add[ci])] = interim_crit[ci, nStage, cj]
        
        pred_treatment_dict.clear()
    
    free(critical_array_pointer)
    free(probBetaBinomial_treatment_pointer)
    free(probBetaBinomial_control_pointer)
    del pred_treatment_dict, pred_total_dict
    return 1    

        
    
def InterimPredictiveProbability(nsim, nArm, nStage, prior, predSuccess, predClinSig, treatment_add, control_add, sim_dataset, 
                                 tps_array, gamma_nsim, gamma_vect, interim_crit, pathdir, effColHeader, patColHeader):
    
    try: 
        
        return CalInterimPredictiveProbability(nsim, nArm, nStage, prior, predSuccess, predClinSig, treatment_add, control_add, sim_dataset, 
                                           tps_array, gamma_nsim, gamma_vect, interim_crit, pathdir, effColHeader, patColHeader)
        
    except:
        
        sys.stdout.write("Oops, fail to calculate the predictive probability")
