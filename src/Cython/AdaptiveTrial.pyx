import cython
# from nt import O_NOINHERIT
cimport cython

import numpy as np
cimport numpy as np

from cython_gsl cimport *
from libc.stdlib cimport malloc, free

# import other packages
import sys
import time
import pandas as pd

DTYPE = np.float64
ctypedef np.float64_t DTYPE_t

@cython.boundscheck(False)
@cython.wraparound(False)
@cython.cdivision(True)
cdef float Trialcheck(float v1, float v2, float v3, float v4, float cval):
    cdef float trt, null
    trt = (v1/(v1 + v2)) - cval
    null = v3/(v3 + v4)
    return 1 if trt > null else 0

@cython.boundscheck(False)
@cython.wraparound(False)
@cython.cdivision(True)
cdef dict output_data(float[:, :, ::1] gamma_vect, int seed, int n1, int n2, float clin_sig, float pred_succ, int[::1] final_data):

    cdef Py_ssize_t i, j, k
    cdef int nsim = 50000
    cdef int bisect_nsim = 500
    cdef int index0 = 0, index1 = 1, bisect_stop = 1, mid_n, min_n, max_n, o_n
    cdef float crit_arr, crit_sum

    # Assume allocation between treatment is equal
    # N1 Treatment
    # N2 Control
    for i in xrange(0, n1 + 1):
        # initialize for the bisection search
        # to find the value meet the successful boundary
        max_n = n2
        min_n = 0
        mid_n = np.rint(max_n/2)
        while max_n > min_n:
            crit_sum = 0
            for k in range(0, bisect_nsim):
                crit_sum += Trialcheck(gamma_vect[index0, i, k], gamma_vect[index1, n1-i, k], gamma_vect[index1, mid_n, k], gamma_vect[index0, n2-mid_n, k], clin_sig)
            crit_arr = crit_sum/bisect_nsim
            if crit_arr < pred_succ:
                max_n = mid_n - 1
                mid_n = np.rint((max_n + min_n)/2)
            elif crit_arr > pred_succ:
                min_n = mid_n + 1
                mid_n = np.rint((min_n + max_n)/2)
            elif crit_arr == pred_succ:
                min_n = mid_n
        # exact verification
        while bisect_stop:
            crit_sum = 0
            for k in range(0, nsim):
                crit_sum += Trialcheck(gamma_vect[index0, i, k], gamma_vect[index1, n1-i, k], gamma_vect[index1, min_n, k], gamma_vect[index0, n2-min_n, k], clin_sig)
            crit_arr = crit_sum/nsim
            if crit_arr > pred_succ:
                if o_n == -1:
                    min_n = min_n + 1
                    bisect_stop = 0
                else:
                    min_n = min_n + 1
                    o_n = 1
            elif crit_arr < pred_succ:
                if o_n == 1:
                    bisect_stop = 0
                else:
                    min_n = min_n - 1
                    o_n = -1
                    
            elif crit_arr == pred_succ:
                min_n = min_n + 1
                bisect_stop == 0
        
        final_data[i] = min_n    



# check trial progress
# return futile, efficacy
# if predictive probability is required, calculate it
# nsim: number of simulations
# n_arm: number of arms
# n_stage: number of stages
# ps_array: patients assignment
# ful, eff: fultility and efficacy boundary
# clin_sig: clinical significance
# sim_dataset: simulated dataset
@cython.boundscheck(False)
@cython.wraparound(False)
@cython.cdivision(True)
cdef trial_progress(int nsim, int seed, int n_arm, int n_stage, double[::1] te_list, int[:, ::1] ps_array, float alloc, float ful, float eff, 
                    float clin_sig, int pred_flag, int pred_num = 20, float pred_success = 0):
    
    cdef Py_ssize_t m, p, q, i, j, k, l, ini, ink, init_arm, init_nsim, success1, success2, fail1, fail2
    cdef Py_ssize_t index0 = 0, index1 = 1, total_index = 2, gamma_nsim = 50000
    cdef float gamma1, gamma2, gamma3, gamma4, sum
    cdef int total1, total2, tps_stage, tps_stop, tps_trt, tps_control
    cdef float tps_alloc
    cdef int pred_trt_add, pred_control_add
    cdef int[::1] add_vect
    cdef dict interim_dict = {}
    cdef int *sim_dataset_pointer = <int *>malloc(n_arm * n_stage * nsim * sizeof(int))
    cdef int[:, :, ::1] sim_dataset = <int[:n_arm, :n_stage, :nsim]> sim_dataset_pointer 
    
    cdef int *tps_array_pointer = <int *>malloc(n_arm * n_stage * nsim * sizeof(int))
    cdef int[:, :, ::1] tps_array= <int[:n_arm, :n_stage, :nsim]> tps_array_pointer
    
    # patients at each stage
    cdef int[::1] ps_array_stage = np.sum(ps_array, axis=0)
    # initialize, all the same
    #tps_array[:, 0, :] = np.repeat(ps_array[:, 0], nsim, axis=0)
    for init_arm in range(0, n_arm): 
        for init_nsim in range(0, nsim):
            tps_array[init_arm, 0, init_nsim] = ps_array[init_arm, 0]
            
    cdef int *futile_pointer = <int *>malloc((n_arm-1) * n_stage * nsim * sizeof(int))
    cdef int[:, :, ::1] futile = <int[:(n_arm-1), :n_stage, :nsim]> futile_pointer
    cdef int *efficacy_pointer = <int *>malloc((n_arm-1) * n_stage * nsim * sizeof(int))
    cdef int[:, :, ::1] efficacy = <int[:(n_arm-1), :n_stage, :nsim]> efficacy_pointer
    cdef int *stop_pointer = <int *>malloc((n_arm-1) * n_stage * nsim * sizeof(int))
    cdef int[:, :, ::1] stop = <int[:(n_arm-1), :n_stage, :nsim]> stop_pointer
    
    cdef int *pred_control_pointer = <int *>malloc(nsim * sizeof(float*))
    cdef int[::1] pred_control = <int[:nsim]> pred_control_pointer

    cdef int *pred_trt_pointer = <int *>malloc((n_arm-1) * nsim * sizeof(float))
    cdef int[:, ::1] pred_trt = <int[:(n_arm-1), :nsim]> pred_trt_pointer
    # cdef int [::1] total_ps = np.sum(ps_array, axis=1)
    # patients at each arm
    # cdef int [:, ::1] tps_array = np.cumsum(ps_array, axis=1)
    
    #cdef float *interim_crit_pointer = <float *>malloc((n_arm-1) * n_stage *nsim * sizeof(int))
    #cdef float [:, :, ::1] interim_crit = <float[:(n_arm-1), :n_stage, :nsim]> interim_crit_pointer
    # cdef DTYPE_t [:, :, ::1] interim_crit = np.empty((n_arm-1, n_stage, nsim))
    cdef gsl_rng *binomial_r = gsl_rng_alloc(gsl_rng_mt19937)
    cdef gsl_rng *point = gsl_rng_alloc(gsl_rng_mt19937)
    gsl_rng_set(binomial_r, seed)
    gsl_rng_set(point, seed)
    cdef int total_patient = np.sum(ps_array, dtype=np.dtype(int))
    cdef int max_tps
    # assign patients for the first stage
    if alloc > 1:
        max_tps = np.rint(total_patient)*(alloc/(1+alloc)) + 1
        if pred_flag == 1:
            max_tps += np.rint(pred_num)*(alloc/(1+alloc)) + 1
    else:
        max_tps = np.rint(total_patient)*(1.0/(1+alloc)) + 1
        if pred_flag == 1:
            max_tps += np.rint(pred_num)*(1.0/(1+alloc)) + 1
    """
    cdef float ***gamma_vect
    gamma_vect = <float ***> malloc(2*sizeof(float **))
    for m in range(0, 2):
        gamma_vect[m] = <float **>malloc(max_tps*sizeof(float *))
        for p in xrange(0, max_tps):
            gamma_vect[m][p] = <float *>malloc(gamma_nsim*sizeof(float))
            for q in xrange(0, gamma_nsim):
                gamma_vect[m][p][q] = gsl_ran_gamma(point, p+1, 1)
    """         
    cdef float *gamma_arr = <float *>malloc(total_index * max_tps * gamma_nsim * sizeof(float))
    cdef float[:, :, ::1] gamma_vect = <float[:total_index, :max_tps, :gamma_nsim]>gamma_arr
    for m in range(0, total_index):
        for p in range(0, max_tps):
            for q in xrange(0, gamma_nsim):
                gamma_vect[m, p, q] = gsl_ran_gamma(point, p+1, 1)
                
    sys.stdout.write("Simulate interim characteristics...")
    for j in range(0, n_stage):    
        # simulate dataset
        for i in range(0, n_arm-1):
            for k in xrange(0, nsim):
                if tps_array[i, j, k] == 0:
                    sim_dataset[i, j, k] == 0
                    continue
                if j == 0:
                    sim_dataset[n_arm-1, j, k] = gsl_ran_binomial(binomial_r, te_list[n_arm-1], tps_array[n_arm-1, j, k])
                if j > 0:
                    sim_dataset[n_arm-1, j, k] = gsl_ran_binomial(binomial_r, te_list[n_arm-1], (tps_array[n_arm-1, j, k] - tps_array[n_arm-1, j-1, k])) + sim_dataset[n_arm-1, j-1, k]
            for k in xrange(0, nsim):
                if tps_array[i, j, k] == 0:
                    sim_dataset[i, j, k] = 0
                    stop[i, j, k] = stop[i, j-1, k]
                    futile[i, j, k] = futile[i, j-1, k]
                    efficacy[i, j, k] = efficacy[i, j-1, k]
                    continue
                # treatment
                if j == 0:
                    sim_dataset[i, j, k] = gsl_ran_binomial(binomial_r, te_list[i], tps_array[i, j, k])
                elif j > 0:
                    sim_dataset[i, j, k] = gsl_ran_binomial(binomial_r, te_list[i], (tps_array[i, j, k] - tps_array[i, j-1, k])) + sim_dataset[i, j-1, k]       
                success1 = sim_dataset[i, j, k]
                fail1 = tps_array[i, j, k] - success1
                # control
                #print "success:%d\n"%sim_dataset[i,j,k]
                #print "total:%d\n"%tps_array[i, j, k]
                success2 = sim_dataset[n_arm-1, j, k]
                fail2 = tps_array[n_arm-1, j, k] - success2  
                #print "success:%d\n"%sim_dataset[n_arm-1,j,k]
                #print "total:%d\n"%tps_array[n_arm-1, j, k]
                if interim_dict.has_key((success1, success2, fail1, fail2)):
                    #interim_crit[i, j, k] = interim_dict[(success1, success2, fail1, fail2)]
                    futile[i, j, k] = int(interim_dict[(success1, success2, fail1, fail2)] < ful)
                    efficacy[i, j, k] = int(interim_dict[(success1, success2, fail1, fail2)] > eff)
                    stop[i, j, k] = int(futile[i, j, k] | efficacy[i, j, k])
                else:
                    sum = 0
                    for l in xrange(0, gamma_nsim):
                        gamma1 = gamma_vect[index0, success1, l]
                        gamma2 = gamma_vect[index1, fail1, l]
                        gamma3 = gamma_vect[index0, success2, l]
                        gamma4 = gamma_vect[index1, fail2, l]
                        sum += Trialcheck(gamma1, gamma2, gamma3, gamma4, clin_sig)
                    interim_dict[(success1, success2, fail1, fail2)] = sum/gamma_nsim
                    futile[i, j, k] = int(interim_dict[(success1, success2, fail1, fail2)] < ful)
                    efficacy[i, j, k] = int(interim_dict[(success1, success2, fail1, fail2)] > eff)
                    stop[i, j, k] = int(futile[i, j, k] | efficacy[i, j, k])
         
        interim_dict.clear()
        if j < n_stage -1:
            # patients to be assigned at a stage
            tps_stage = ps_array_stage[j]
            for ink in xrange(0, nsim):
                tps_stop = np.sum(stop[:, j, ink])
                if tps_stop == n_arm-1:
                    tps_array[:, j+1, ink] = 0
                else:
                    # reallocate the patients
                    # How many people needed to be re-assigned
                    # tps_stage = np.sum(np.array(stop[:, j, ink])* np.array(ps_array[0:n_arm-1, j+1]))
                    tps_alloc = sqrt(n_arm - 1 - tps_stop)
                    # treatment arm and control arm
                    tps_trt = np.rint(tps_stage * 1/(n_arm-1 - tps_stop + tps_alloc))
                    tps_control = tps_stage - tps_trt * (n_arm -1 - tps_stop)
                    for ini in range(0, n_arm-1):
                        if stop[ini, j, ink] != 1:
                            tps_array[ini, j+1, ink] =  tps_array[ini, j, ink] + tps_trt*(1-stop[ini, j, ink]) 
                        else: 
                            tps_array[ini, j+1, ink] = 0
                    tps_array[n_arm-1, j+1, ink] = tps_array[n_arm-1, j, ink] + tps_control
        
        if j == n_stage - 1 and pred_flag == 1:
            # calculate patients added
            for ink in xrange(0, nsim):
                # treatment stop for futility
                tps_stop = np.sum(futile[:, j, ink])
                tps_alloc = sqrt(n_arm - 1 - tps_stop)
                if tps_stop != n_arm-1:
                    # if not total stop, calculate patient being assigned
                    pred_trt_add = np.rint(pred_num * 1/(n_arm - 1 - tps_stop + tps_alloc))
                    pred_control_add = pred_num - pred_trt_add * (n_arm - 1 - tps_stop)
                    for ini in range(0, n_arm-1):
                        pred_trt[ini, ink] = pred_trt_add*(1 -futile[ini, j, ink])
                    pred_control[ink] = pred_control_add 
                else:
                    pred_trt[ini, ink] = 0
                    pred_control[ink] = 0 
                    
    gsl_rng_free(binomial_r)
    gsl_rng_free(point)
    sys.stdout.write("Calculate futility and efficacy...")
    """
    cdef np.ndarray[np.uint8_t, ndim = 3] futile = interim_crit < ful
    cdef np.ndarray[np.uint8_t, ndim = 3] efficacy = interim_crit > eff
    cdef np.ndarray[np.uint8_t, ndim = 3] each_stop = np.logical_or(ful, eff)
    cdef np.ndarray[np.uint8_t, ndim = 2] stop = np.all(each_stop, axis=0)
    interim_crit_array = np.asarray(interim_crit, dtype=np.float64)
    # print interim_crit_array
    futile = interim_crit_array < ful
    efficacy = interim_crit_array > eff
    each_stop = np.logical_or(futile, efficacy)
    stop = np.all(each_stop, axis=0)
    """
    del interim_dict
    
    con_futile = np.cumsum(futile, axis=1, dtype=bool)
    con_efficacy = np.cumsum(efficacy, axis=1, dtype=bool)
    cdef np.ndarray[DTYPE_t, ndim = 2] con_futile_mean = np.sum(con_futile, axis=2, dtype=np.float64)/nsim*100
    cdef np.ndarray[DTYPE_t, ndim = 2] con_efficacy_mean = np.sum(con_efficacy, axis=2, dtype=np.float64)/nsim*100
    cdef np.ndarray[DTYPE_t, ndim = 2] con_continuous_mean = 100 - con_efficacy_mean - con_futile_mean
         
    cdef Py_ssize_t ci, cj, ck, cl, cm, cp, cq, success_index_copy, ck_copy, cm_copy
    cdef int beta_index1, beta_index2, beta_index3, beta_index4, success_index = 0
    # obs_succ_control, trt: observed data
    # pred_trt_add, control_add: patients added
    # pred_trt, pred_control: pred_data + observed_data
    cdef int pred_trt_total, pred_control_total, pred_succ, obs_succ_control, obs_succ_trt, index_trt, index_control
    cdef int pred_num_control = np.rint(pred_num)*(alloc/(1+alloc)) + 1
    cdef int pred_num_trt =  pred_num + 2 - pred_num_control
    cdef int possible_scene 
    possible_scene = int(pow((n_stage + 1), (n_arm - 1)))
    cdef float constant_choose_control, constant_choose_trt, cpower_sum
    # new patients added
    # total index
    cdef dict critical_dataset = {}
    cdef dict pred_control_dict = {}
    cdef dict pred_trt_dict = {}
    cdef dict pred_total_dict = {}

    cdef float *prob_control_pointer = <float *>malloc(pred_num_control * nsim * sizeof(float))
    cdef float[:, ::1] prob_control = <float[:pred_num_control, :nsim]> prob_control_pointer

    cdef float *prob_trt_pointer = <float *>malloc(pred_num_trt * nsim * sizeof(float))
    cdef float[:, ::1] prob_trt = <float[:pred_num_trt, :nsim]> prob_trt_pointer
    
    cdef float *cpower_array_pointer = <float *>malloc((n_arm-1) * nsim * sizeof(float))
    cdef float[:, ::1] cpower_array = <float[:(n_arm-1), :nsim]> cpower_array_pointer
    
    cdef float *cpower_array_per_pointer = <float *>malloc((n_arm-1) * nsim * sizeof(float))
    cdef float[:, ::1] cpower_array_per = <float[:(n_arm-1), :nsim]> cpower_array_per_pointer
    
    cdef int *critical_array_pointer = <int *>malloc(possible_scene * max_tps * sizeof(int))
    cdef int[:, ::1] critical_array = <int[:possible_scene, :max_tps]> critical_array_pointer
    
    cdef np.ndarray [DTYPE_t, ndim = 1] con_power = np.empty(n_arm - 1)
    cdef np.ndarray [DTYPE_t, ndim = 1] con_power_per = np.empty(n_arm - 1)
    # calculate posterior predictive probability
    if pred_flag == 1:
        sys.stdout.write("Calculate posterior predictive probability...") 
        sys.stdout.write("Retrieve the dataset...")
        
        for ck in xrange(0, nsim):    
            
            obs_succ_control = sim_dataset[n_arm-1, n_stage-1, ck]
            pred_control_total = tps_array[n_arm-1, n_stage-1, ck] + pred_control[ck]
            if pred_control_dict.has_key((obs_succ_control, pred_control[ck])):
                ck_copy = pred_control_dict[(obs_succ_control, pred_control[ck])]
                for cl in xrange(0, pred_control[ck] + 1):
                    prob_control[cl, ck] = prob_control[cl, ck_copy]
            else:
                for cl in xrange(0, pred_control[ck] + 1):

                    beta_index1 = cl + obs_succ_control
                    beta_index2 = cl
                    beta_index3 = tps_array[n_arm-1, n_stage-1, ck] + pred_control[ck] - cl - obs_succ_control
                    beta_index4 = pred_control[ck] - cl
                    #prob_control_vector[cl] = gsl_sf_choose(pred_control[ck], cl)*gsl_sf_beta(beta_index1, beta_index2)/gsl_sf_beta(beta_index3, beta_index4)
                    prob_control[cl, ck] =  gsl_sf_choose(beta_index1, beta_index2) * gsl_sf_choose(beta_index3, beta_index4)/gsl_sf_choose(pred_control_total + 1 , pred_control[ck])
                pred_control_dict[(obs_succ_control, pred_control[ck])] = ck
                
        del pred_control_dict    
        sys.stdout.write("Calculate for treatment...")
        # calculate probability for treatment
        # for control arm
        for ci in range(0, n_arm-1):
            for ck in xrange(0, nsim):
                # print "arm: %d, sim: %d, stop:%d"%(ci, ck, stop[ci, n_stage-1, ck])
                if futile[ci, n_stage-1, ck] == 1:
                    cpower_array[ci, ck] = 0
                    continue
                elif efficacy[ci, n_stage-1, ck] == 1:
                    # pred treatment total 
                    # pred control total
                    pred_control_total = tps_array[n_arm-1, n_stage-1, ck] + pred_control[ck]
                    pred_trt_total = max(tps_array[ci, :, ck]) + pred_trt[ci, ck]
                    if not critical_dataset.has_key((pred_trt_total, pred_control_total)): 
                        output_data(gamma_vect, seed, pred_trt_total, pred_control_total, clin_sig, pred_success, critical_array[success_index, :])        
                        critical_dataset[(pred_trt_total, pred_control_total)] = success_index
                        success_index += 1
                        # print success_index
                    # observed success in control and treatment
                    obs_succ_control = sim_dataset[n_arm-1, n_stage-1, ck]
                    obs_succ_trt = max(sim_dataset[ci, :, ck])
                    # simulated success for the added patients
                    # pred_trt_dict[(obs_succ_trt, pred_trt[ci, ck])] = []
                    if pred_trt_dict.has_key((obs_succ_trt, pred_trt[ci, ck])):
                        ck_copy = pred_trt_dict[(obs_succ_trt, pred_trt[ci, ck])]
                        for cm in xrange(0, pred_trt[ci, ck] + 1):
                            prob_trt[cm, ck] = prob_trt[cm, ck_copy]
                    else:
                        for cm in xrange(0, pred_trt[ci, ck] + 1):
                            beta_index1 = cm + obs_succ_trt
                            beta_index2 = cm
                            beta_index3 = max(tps_array[ci, :, ck]) + pred_trt[ci, ck] - cm - obs_succ_trt
                            beta_index4 = pred_trt[ci, ck] - cm
                            prob_trt[cm, ck] =  gsl_sf_choose(beta_index1, beta_index2) * gsl_sf_choose(beta_index3, beta_index4)/gsl_sf_choose(pred_trt_total + 1, pred_trt[ci, ck])                   
                        pred_trt_dict[(obs_succ_trt, pred_trt[ci, ck])] = ck
                    # print "%d after Phase 2, %d added for control" %(tps_array[n_arm-1, n_stage-1, ck], pred_control[ck])
                    # print "%d after phase 2, %d added for treatment"%(tps_array[ci, n_stage-1, ck], pred_trt[ci, ck])

                    if pred_total_dict.has_key((obs_succ_control, obs_succ_trt, pred_control[ck], pred_trt[ci, ck])):
                        cpower_array[ci, ck] = pred_total_dict[(obs_succ_control, obs_succ_trt, pred_control[ck], pred_trt[ci, ck])]
                        cpower_array_per[ci, ck] = pred_total_dict[(obs_succ_control, obs_succ_trt, pred_control[ck], pred_trt[ci, ck])]/pred_trt_total
                    else:
                        cpower_sum = 0.0
                        for cm in xrange(0, pred_trt[ci, ck] + 1):
                            index_trt = obs_succ_trt + cm
                            success_index_copy = critical_dataset[(pred_trt_total, pred_control_total)]
                            cm_copy = critical_array[success_index_copy, index_trt] - obs_succ_control
                            if cm_copy < 0:
                                cm_copy = 0
                            elif cm_copy > pred_control[ck]:
                                cm_copy = pred_control[ck] + 1
                            for cl in xrange(0, cm_copy):
                                cpower_sum += prob_control[cl, ck] * prob_trt[cm, ck]
                        cpower_array[ci, ck] = cpower_sum
                        cpower_array_per[ci, ck] = cpower_sum/pred_trt_total
                        pred_total_dict[(obs_succ_control, obs_succ_trt, pred_control[ck], pred_trt[ci, ck])] = cpower_array[ci, ck]
                else:
                    # pred treatment total 
                    # pred control total
                    pred_control_total = tps_array[n_arm-1, n_stage-1, ck] + pred_control[ck]
                    pred_trt_total = tps_array[ci, n_stage-1, ck] + pred_trt[ci, ck]
                    if not critical_dataset.has_key((pred_trt_total, pred_control_total)): 
                        output_data(gamma_vect, seed, pred_trt_total, pred_control_total, clin_sig, pred_success, critical_array[success_index, :])        
                        critical_dataset[(pred_trt_total, pred_control_total)] = success_index
                        success_index += 1
                        # print success_index
                    # observed success in control and treatment
                    obs_succ_control = sim_dataset[n_arm-1, n_stage-1, ck]
                    obs_succ_trt = sim_dataset[ci, n_stage-1, ck]
                    # simulated success for the added patients
                    # pred_trt_dict[(obs_succ_trt, pred_trt[ci, ck])] = []
                    if pred_trt_dict.has_key((obs_succ_trt, pred_trt[ci, ck])):
                        ck_copy = pred_trt_dict[(obs_succ_trt, pred_trt[ci, ck])]
                        for cm in xrange(0, pred_trt[ci, ck] + 1):
                            prob_trt[cm, ck] = prob_trt[cm, ck_copy]
                    else:
                        for cm in xrange(0, pred_trt[ci, ck] + 1):
                            beta_index1 = cm + obs_succ_trt
                            beta_index2 = cm
                            beta_index3 = tps_array[ci, n_stage-1, ck] + pred_trt[ci, ck] - cm - obs_succ_trt
                            beta_index4 = pred_trt[ci, ck] - cm
                            prob_trt[cm, ck] =  gsl_sf_choose(beta_index1, beta_index2) * gsl_sf_choose(beta_index3, beta_index4)/gsl_sf_choose(pred_trt_total + 1, pred_trt[ci, ck])                   
                        pred_trt_dict[(obs_succ_trt, pred_trt[ci, ck])] = ck
                    # print "%d after Phase 2, %d added for control" %(tps_array[n_arm-1, n_stage-1, ck], pred_control[ck])
                    # print "%d after phase 2, %d added for treatment"%(tps_array[ci, n_stage-1, ck], pred_trt[ci, ck])

                    if pred_total_dict.has_key((obs_succ_control, obs_succ_trt, pred_control[ck], pred_trt[ci, ck])):
                        cpower_array[ci, ck] = pred_total_dict[(obs_succ_control, obs_succ_trt, pred_control[ck], pred_trt[ci, ck])]
                        cpower_array_per[ci, ck] = pred_total_dict[(obs_succ_control, obs_succ_trt, pred_control[ck], pred_trt[ci, ck])]/pred_trt_total
                    else:
                        cpower_sum = 0.0
                        for cm in xrange(0, pred_trt[ci, ck] + 1):
                            index_trt = obs_succ_trt + cm
                            success_index_copy = critical_dataset[(pred_trt_total, pred_control_total)]
                            cm_copy = critical_array[success_index_copy, index_trt] - obs_succ_control
                            if cm_copy < 0:
                                cm_copy = 0
                            elif cm_copy > pred_control[ck]:
                                cm_copy = pred_control[ck] + 1
                            for cl in xrange(0, cm_copy):
                                cpower_sum += prob_control[cl, ck] * prob_trt[cm, ck]
                        cpower_array[ci, ck] = cpower_sum
                        cpower_array_per[ci, ck] = cpower_sum/pred_trt_total
                        pred_total_dict[(obs_succ_control, obs_succ_trt, pred_control[ck], pred_trt[ci, ck])] = cpower_array[ci, ck] 
            pred_total_dict.clear()
        
        del critical_dataset, pred_trt_dict, pred_total_dict 
         
        sys.stdout.write("Generate beta-binomial variables...")  

        for ci in range(0, n_arm-1):
            con_power[ci] = np.sum(np.array(cpower_array[ci, :]))/(nsim - np.sum(np.array(futile[ci, n_stage-1, :])))*100   
            con_power_per[ci] = np.sum(np.array(cpower_array_per[ci, :]))/(nsim - np.sum(np.array(futile[ci, n_stage-1, :])))*100

        free(prob_control_pointer)     
        free(prob_trt_pointer)
        free(cpower_array_pointer)
        free(critical_array_pointer)
    
    free(futile_pointer)
    free(efficacy_pointer)   
    
    # this could optimization
    sys.stdout.write("Summarize results...")
    
    # calculate conditional futile, efficacy, and stop for each time
    """
    cdef np.ndarray[DTYPE_t, ndim = 3] con_futile = np.cumsum(futile, axis=1, dtype=bool)
    cdef np.ndarray[DTYPE_t, ndim = 3] con_efficacy = np.cumsum(efficacy, axis=1, dtype=bool)
    """
    # cdef np.ndarray[DTYPE_t, ndim = 1] stop_mean = np.sum(stop, axis=1, dtype=np.float64)/nsim*100
    
    sys.stdout.write("Output results...")
    del con_futile, con_efficacy
    """
    for m in range(0, 2):
        for p in range(0, max_tps):
            free(gamma_vect[m][p])
        free(gamma_vect[m]) 
    free(gamma_vect)
    """
    free(gamma_arr)
    free(stop_pointer)
    free(sim_dataset_pointer)
    free(tps_array_pointer)
    # free(interim_crit_pointer)
    return con_futile_mean, con_efficacy_mean, con_continuous_mean, con_power, con_power_per

# trial simulation(nseed, nsim, out_dir, te_list, clinical_sig, futile_cut, efficacy_cut,
#                                     alloc, ps_array, efficacy_bound, n_group, n_stage)
# initialize the trial simulation here
# include trial data generation, trial progress simulation and predictive probability calculation
# alloc for this version is not used


def trial_simulation(nsim, seed, n_arm, n_stage, te_list, ps_array, alloc, add_flag, ful, eff, clin_sig, pred_flag, *args):

    if seed == -1:
        seed = np.random.randint(1, 12345, size=1)
    if pred_flag == 1:
        pred_num = args[0][0]
        pred_success = args[0][1]
        if len(args) == 4:
            load_file_flag = args[0][3]
            CVLfile = args[0][2]
        else:
            load_file_flag = args[0][2]
        if load_file_flag == 1:
            CVLfile_type = CVLfile.rsplit(".",1)[1]
            sys.stdout.write("read critical value look up table...")
            if CVLfile_type == "p":
                critical_dataset = pd.read_pickle(CVLfile)
            elif CVLfile_type == "csv":
                critical_dataset = pd.read_csv(CVLfile)
        """
        elif load_file_flag == -1:
            sys.stdout.write("Generate the critical value look up table...")
            critical_dataset = CVL.output(seed, num1, num2, clin_sig, CVLfile)
        else:
            sys.stdout.write("Generate the critical value look up table...")
            critical_dataset = CVL.output(seed, num1, num2, clin_sig, ".")
        """
    else:
        pred_num = 20
        pred_success = 0
    # cumulative sum of patients by stage
    #  cum_ps = np.cumsum(ps_array, axis=1)
    
    """
    # get the maximum possible to generate the gamma random variables 
    max_n = max(total_ps) + predict
    gamma_vect = gammag.generate_gamma(int(max_n), 100000)
    print "Generate the critical value look-up table...\n"
    critical_dataset = cvl.output(100000, total_ps[0]+predict, total_ps[1]+predict, out_dir)
    """
    # get futility, efficacy, stop for each arm and stop totally
    sys.stdout.write("Start Simulation")
    
    futile, efficacy, continuous, cpower, cpower_per = trial_progress(nsim, seed, n_arm, n_stage, te_list, ps_array, alloc, ful, eff, clin_sig,
                                                       pred_flag, pred_num, pred_success)
    

    print futile
    print "efficacy:"
    print efficacy
    print cpower
    print cpower_per
    """
    # calculate conditional futile, efficacy, and stop for each time
    con_futile = np.cumsum(futile, axis=1, dtype=bool)
    con_efficacy = np.cumsum(efficacy, axis=1, dtype=bool)
    # each_stop = futile*-1 + efficacy
    obs0 = sim_dataset[0, 2, :]
    obsa = sim_dataset[1:, 2, :]

    crit_975 = critical_dataset["critical"] > efficacy_bound
    new_crit_975 = critcreate(crit_975, total_ps)
    if predict != 0:
        print "Calculate posterior predictive probability...\n"
        cp_mean = cpower(nsim, n_group, obs0, obsa, new_crit_975, total_ps, predict)
    output_dict = {}
    name_stage = ["stageI", "stageII", "stageIII"]
    columns = ["P0", "P1", "P2", "P3", "F1", "F2", "F3", "E1", "E2", "E3", "C1", "C2", "C3", "CP1", "CP2", "CP3"]
    for i in range(n_stage):
        group_mean = (np.sum(sim_dataset[:, i, :], axis=1, dtype=np.float64)/nsim)/cum_ps[:, i]*100
        output_dict[name_stage[i]] = np.concatenate([group_mean, con_futile_mean, con_efficacy_mean, con_continuous,
                                                     cp_mean])
    df = pd.DataFrame(output_dict).transpose()
    del gamma_vect
    """
    return