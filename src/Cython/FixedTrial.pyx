import cython
cimport cython

import numpy as np
cimport numpy as np

from cython.parallel cimport prange
from cython_gsl cimport *
from libc.stdlib cimport malloc, free

# import other packages
import sys
import pandas as pd
import GSLCriticalValue as CriticalValue

DTYPE = np.float64
ctypedef np.float64_t DTYPE_t

@cython.boundscheck(False)
@cython.wraparound(False)
@cython.cdivision(True)
cdef float Trialcheck(float v1, float v2, float v3, float v4, float cval) nogil:
    cdef float trt, null
    trt = (v1/(v1 + v2)) - cval
    null = v3/(v3 + v4)
    return 1 if trt > null else 0

# simulate trial data
# nsim: number of simulations
# n_arm: number of arms
# n_stage: number of stages
# te_list: treatment effects for each group:, [p0, p1, p2... pn]
# ps_array: patients at each group at each stage
@cython.boundscheck(False)
@cython.wraparound(False)
@cython.cdivision(True)
cdef trial_data(int nsim, int n_arm, int n_stage, np.ndarray[DTYPE_t, ndim = 1] te_list, int [:,::1] ps_array):
    
    cdef Py_ssize_t i, j, k
    cdef int [:, :, ::1]trial_array = np.empty([n_arm, n_stage, nsim], dtype=int)
    cdef int [:, :, ::1]final_data = np.empty([n_arm, n_stage, nsim], dtype=int)
    
    # simulate the data
    for i in range(0, n_arm):
        for j in range(0, n_stage):
            for k in xrange(0, nsim):
                trial_array[i, j, k] = np.random.binomial(ps_array[i, j], te_list[i], 1)
    # cumulative for the stage
    final_data = np.cumsum(trial_array, axis=1)
    del trial_array
    return final_data


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
cdef trial_progress(int nsim, int seed, int n_arm, int n_stage, int[:, ::1] ps_array, float alloc, float ful, float eff, 
                    float clin_sig, int[:, :, ::1] sim_dataset, int pred_flag, int pred_num = 20, float pred_success = 0):
    
    cdef Py_ssize_t m, p, q, i, j, k, l, success1, success2, fail1, fail2, index0 = 0, index1 = 1, total_index = 2, gamma_nsim = 50000
    cdef float gamma1, gamma2, gamma3, gamma4, sum
    cdef int total1, total2
    cdef dict interim_dict = {}
    cdef int [::1] total_ps = np.sum(ps_array, axis=1)
    # patients at each arm
    cdef int [:, ::1] tps_array = np.cumsum(ps_array, axis=1)
    cdef DTYPE_t [:, :, ::1] interim_crit = np.empty((n_arm-1, n_stage, nsim))
    cdef gsl_rng *point = gsl_rng_alloc(gsl_rng_mt19937)
    
    cdef int max_tps = max(total_ps) + 1
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
        for p in prange(0, max_tps, nogil=True):
            for q in range(0, gamma_nsim):
                gamma_vect[m, p, q] = gsl_ran_gamma(point, p+1, 1)
    """
    sys.stdout.write("Simulate interim characteristics...")
    for j in range(0, n_stage):    
        for i in range(0, n_arm-1):
            for k in xrange(0, nsim):
                # treatment
                success1 = sim_dataset[i, j, k]
                fail1 = tps_array[i, j] - success1
                # control
                success2 = sim_dataset[n_arm-1, j, k]
                fail2 = tps_array[n_arm-1, j] - success2  
                if interim_dict.has_key((success1, success2, fail1, fail2)):
                    interim_crit[i, j, k] = interim_dict[(success1, success2, fail1, fail2)]
                else:
                    sum = 0
                    for l in prange(0, gamma_nsim, nogil=True):
                        """
                        sum += CriticalValue.check(gamma_vect[index0][success1][l], gamma_vect[index1][fail1][l],
                                                    gamma_vect[index1][success2][l], gamma_vect[index0][fail2][l], clin_sig)
                        
                        gamma1 = gamma_vect[index0, success1, l]
                        gamma2 = gamma_vect[index1, fail1, l]
                        gamma3 = gamma_vect[index0, success2, l]
                        gamma4 = gamma_vect[index1, fail2, l]
                        """
                        gamma1 = gamma_vect[index0][success1][l]
                        gamma2 = gamma_vect[index1][fail1][l]
                        gamma3 = gamma_vect[index0][success2][l]
                        gamma4 = gamma_vect[index1][fail2][l]
                        sum += Trialcheck(gamma1, gamma2, gamma3, gamma4, clin_sig)
                    interim_dict[(success1, success2, fail1, fail2)] = sum/gamma_nsim
                    interim_crit[i, j, k] = interim_dict[(success1, success2, fail1, fail2)]
         
        interim_dict.clear()
    
    for m in range(0, 2):
        for p in range(0, max_tps):
            free(gamma_vect[m][p])
        free(gamma_vect[m]) 
    free(gamma_vect)
    #free(gamma_vect)
    # free(gamma_arr)
    # free the pointer
    gsl_rng_free(point)
    
    sys.stdout.write("Calculate futility and efficacy...")
    """
    cdef np.ndarray[np.uint8_t, ndim = 3] futile = interim_crit < ful
    cdef np.ndarray[np.uint8_t, ndim = 3] efficacy = interim_crit > eff
    cdef np.ndarray[np.uint8_t, ndim = 3] each_stop = np.logical_or(ful, eff)
    cdef np.ndarray[np.uint8_t, ndim = 2] stop = np.all(each_stop, axis=0)
    """
    interim_crit_array = np.asarray(interim_crit, dtype=np.float64)
    # print interim_crit_array
    futile = interim_crit_array < ful
    efficacy = interim_crit_array > eff
    each_stop = np.logical_or(futile, efficacy)
    stop = np.all(each_stop, axis=0)
    
    del interim_dict, interim_crit
                
    cdef Py_ssize_t ci, cj, ck, cl, cm, cp, cq
    cdef int beta_index1, beta_index2, beta_index3, beta_index4
    # obs_succ_control, trt: observed data
    # pred_trt_add, control_add: patients added
    # pred_trt, pred_control: pred_data + observed_data
    cdef int pred_succ, obs_succ_control, obs_succ_trt, index_trt, index_control 
    # new patients added
    cdef int pred_trt_add = np.rint(pred_num*1/(alloc + n_arm - 1))
    cdef int pred_control_add = pred_num - (n_arm-1)*pred_trt_add
    # total patients 
    cdef int pred_trt = pred_trt_add + total_ps[0]
    cdef int pred_control = pred_control_add + total_ps[n_arm - 1]
    # total index
    cdef dict pred_control_dict = {}
    cdef dict pred_trt_dict = {}
    cdef dict pred_total_dict = {}
    # create memoryview
    # cdef int [:, ::1] sim_success = sim_dataset[:, n_stage-1, :]
    cdef int *sim_success_pointer = <int *>malloc(n_arm * nsim * sizeof(int))
    cdef int [:, ::1] sim_success = <int[:n_arm, :nsim]> sim_success_pointer
    sim_success = sim_dataset[:, n_stage-1, :]
    cdef float *prob_control_pointer = <float *>malloc((pred_control_add+1) * nsim * sizeof(float*))
    cdef float[:, ::1] prob_control = <float[:(pred_control_add+1), :nsim]> prob_control_pointer

    cdef float *prob_trt_pointer = <float *>malloc((pred_trt_add+1) * sizeof(float))
    cdef float [::1] prob_trt = <float[:(pred_trt_add+1)]> prob_trt_pointer

    cdef float *cpower_array_pointer = <float *>malloc((n_arm-1) * nsim * sizeof(float*))
    cdef float [:, ::1]cpower_array = <float[:(n_arm-1), :nsim]> cpower_array_pointer

    #conditional array observations
    cdef float [::1] cpower_obs
    
    # cdef np.ndarray [dtype=float, ndim = 1] con_power = np.empty(n_arm-1)
    # calculate posterior predictive probability
    if pred_flag == 1:
        sys.stdout.write("Calculate posterior predictive probability...") 
        critical_dataset = CriticalValue.output(seed, pred_trt, pred_control, clin_sig, ".")        
        critical_dataset["success"] = critical_dataset["critical"] > pred_success
        sys.stdout.write("Retrieve the dataset...")
        # for control arm
        for cl in xrange(0, pred_control_add + 1):
            for ck in xrange(0, nsim):
                obs_succ_control = sim_success[n_arm-1, ck]
                if pred_control_dict.has_key(obs_succ_control):
                    prob_control[cl, ck] = pred_control_dict[obs_succ_control]
                else:
                    pred_succ = cl + obs_succ_control
                    beta_index1 = 1 + pred_succ
                    beta_index2 = 1 + pred_control - pred_succ
                    beta_index3 = 1 + obs_succ_control
                    beta_index4 = 1 + total_ps[n_arm-1] - obs_succ_control
                    prob_control[cl, ck] = gsl_sf_choose(pred_control_add, cl)*gsl_sf_beta(beta_index1, beta_index2)/gsl_sf_beta(beta_index3, beta_index4)
                    pred_control_dict[obs_succ_control] = prob_control[cl, ck]
            pred_control_dict.clear()
        del pred_control_dict    
        sys.stdout.write("Generate beta-binomial variables...")  
        # for treatment arm
        for ci in range(0, n_arm-1):
            for cj in xrange(0, nsim):
                obs_succ_control = sim_success[n_arm-1, cj]
                obs_succ_trt = sim_success[ci, cj]
                if pred_trt_dict.has_key(obs_succ_trt):
                    prob_trt = pred_trt_dict[obs_succ_trt]
                else:
                    # simulated success for the added patients
                    for cm in prange(0, pred_trt_add+1, nogil=True):
                        pred_succ = cm + obs_succ_trt
                        beta_index1 = 1 + pred_succ
                        beta_index2 = 1 + pred_trt - pred_succ
                        beta_index3 = 1 + obs_succ_trt
                        beta_index4 = 1 + total_ps[ci] - obs_succ_trt
                        prob_trt[cm] = gsl_sf_choose(pred_trt_add, cm)*gsl_sf_beta(beta_index1, beta_index2)/gsl_sf_beta(beta_index3, beta_index4)
                    pred_trt_dict[obs_succ_trt] = prob_trt
                if pred_total_dict.has_key((obs_succ_control, obs_succ_trt)):
                    cpower_array[ci, cj] = pred_total_dict[(obs_succ_control, obs_succ_trt)]
                else:
                    index_trt = obs_succ_trt + pred_trt_add
                    index_control = obs_succ_control + pred_control_add
                    crit_mat = critical_dataset.loc[(slice(obs_succ_trt, index_trt), slice(obs_succ_control, index_control)),:]["success"]
                    cpower_obs = np.repeat(prob_trt, pred_control_add + 1)*np.tile(prob_control[:, cj], pred_trt_add + 1)
                    cpower_array[ci, cj] = np.sum(cpower_obs*crit_mat)
                    pred_total_dict[(obs_succ_control, obs_succ_trt)] = cpower_array[ci, cj]
        
        del critical_dataset, pred_trt_dict, pred_total_dict 
    
        con_power = np.sum(cpower_array, axis=1)/nsim*100   
        free(prob_control_pointer)     
        free(prob_trt_pointer)
        free(cpower_array_pointer)
        free(sim_success_pointer)
    # this could optimization
    sys.stdout.write("Summarize results...")
    
    # calculate conditional futile, efficacy, and stop for each time
    """
    cdef np.ndarray[DTYPE_t, ndim = 3] con_futile = np.cumsum(futile, axis=1, dtype=bool)
    cdef np.ndarray[DTYPE_t, ndim = 3] con_efficacy = np.cumsum(efficacy, axis=1, dtype=bool)
    """
    con_futile = np.cumsum(futile, axis=1, dtype=bool)
    con_efficacy = np.cumsum(efficacy, axis=1, dtype=bool)
    cdef np.ndarray[DTYPE_t, ndim = 2] con_futile_mean = np.sum(con_futile, axis=2, dtype=np.float64)/nsim*100
    cdef np.ndarray[DTYPE_t, ndim = 2] con_efficacy_mean = np.sum(con_efficacy, axis=2, dtype=np.float64)/nsim*100
    cdef np.ndarray[DTYPE_t, ndim = 2] con_continuous_mean = 100 - con_efficacy_mean - con_futile_mean
    cdef np.ndarray[DTYPE_t, ndim = 1] stop_mean = np.sum(stop, axis=1, dtype=np.float64)/nsim*100
    
    sys.stdout.write("Output results...")
    del con_futile, con_efficacy, cpower_obs, sim_success
    return con_futile_mean, con_efficacy_mean, con_continuous_mean, stop_mean, con_power

# trial simulation(nseed, nsim, out_dir, te_list, clinical_sig, futile_cut, efficacy_cut,
#                                     alloc, ps_array, efficacy_bound, n_group, n_stage)
# initialize the trial simulation here
# include trial data generation, trial progress simulation and predictive probability calculation
# alloc for this version is not used


def trial_simulation(nsim, seed, n_arm, n_stage, te_list, ps_array, alloc, add_flag, ful, eff, clin_sig, pred_flag, *args):

    if seed != -1:
        np.random.seed(seed)
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
    # generate the trial outcomes
    sys.stdout.write("Generate the trial dataset...")
    sim_dataset = trial_data(nsim, n_arm, n_stage, te_list, ps_array)
    
    # get futility, efficacy, stop for each arm and stop totally
    sys.stdout.write("Calculate the futility and efficacy...")
    
    futile, efficacy, continuous, stop, cpower = trial_progress(nsim, seed, n_arm, n_stage, ps_array, alloc, ful, eff, clin_sig,
                                                       sim_dataset, pred_flag, pred_num, pred_success)
    

    print futile, cpower
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
