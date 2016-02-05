import cython
cimport cython

import numpy as np
cimport numpy as np

from libcpp.vector cimport vector

# import other packages
import sys
# import os
import pandas as pd
from scipy.special import beta
from scipy.misc import comb
# import GammaGenerate as GammaG
# from datetime import datetime
import CriticalValue as CriticalValue

DTYPE = np.float64
ctypedef np.float64_t DTYPE_t

# simulate trial data
# nsim: number of simulations
# n_arm: number of arms
# n_stage: number of stages
# te_list: treatment effects for each group:, [p0, p1, p2... pn]
# ps_array: patients at each group at each stage
cdef trial_data(int nsim, int n_arm, int n_stage, np.ndarray[DTYPE_t, ndim = 1] te_list, np.ndarray[DTYPE_t, ndim = 3] ps_array):
    
    cdef Py_ssize_t i, j, k
    cdef np.ndarray[DTYPE_t, ndim = 3] trial_array = np.empty([n_arm, n_stage, nsim])
    
    for i in range(0, n_arm):
        for j in range(0, n_stage):
            for k in xrange(0, nsim):
                trial_array[i, j, k] = np.random.binomial(ps_array[i, j], te_list[i], 1)
    # cumulative for the stage
    final_data = np.cumsum(trial_array, axis=1)
    del trial_array
    return final_data

# trial_progress(nsim, clinical_sig, futile_cut, efficacy_cut, sim_dataset,
#                 gamma_vect, n_group, n_stage)
# check trial progress
# use futile_cut, efficacy cut


cdef trial_progress(int nsim, int n_arm, int n_stage, np.ndarray[DTYPE_t, ndim = 3] ps_array, float ful, float eff, 
                    float clin_sig, np.ndarray[DTYPE_t, ndim = 3] sim_dataset, bool pred_flag, **kwargs):
    
    cdef Py_ssize_t k, j, i, m, p, q, ci, cj
    cdef int success1, success2, total1, total2
    cdef int gamma_nsim = 50000
    cdef int index = 0, index = 1
    cdef dict interim_dict = {}
    cdef np.ndarray[DTYPE_t, ndim = 1] total_ps = np.sum(ps_array, axis=1)
    cdef np.ndarray[DTYPE_t, ndim = 1] tps_array = np.cumsum(ps_array, axis=1)
    cdef np.ndarray[DTYPE_t, ndim = 3] interim_crit = np.empty([n_arm-1, n_stage, nsim])
    cdef np.ndarray[DTYPE_t, ndim = 3] cpower_array = np.empty([n_arm-1, nsim])
    cdef np.ndarray[DTYPE_t, ndim = 3] interim_crit = np.empty([n_arm-1, n_stage, nsim]):
    
    # total number of patients at each stage    
    # total_ps = np.sum(ps_array, axis=1)
    # tps_array = np.cumsum(ps_array, axis=1)
    # generate a gamma table
    cdef np.ndarray[DTYPE_t, ndim = 1] gamma_view = np.empty(gamma_nsim)
    cdef vector[int] gamma_list
    
    cdef float*** gamma_vect
    gamma_vect = <float ***> malloc(2*sizeof(float**))
    for m in range(0, 2):
        gamma_vect[m] = <float **>malloc(n*sizeof(float*))
        #for p in range(0, n):
        #gamma_vect[m][p] = <float *>malloc(gamma_nsim*sizeof(float))
        # gamma_view = np.random.gamma(p+1,size=nsim)
        # for q in xrange(0, nsim):
        # gamma_vect[m][p][q] = gamma_view[q]
    
    for i in range(0, n_arm-1):    
        
        for j in range(0, n_stage):
            
            for k in xrange(0, nsim):
            
                success1 = int(sim_dataset[0, j, k])
                fail1 = int(tps_array[0, j]) - success1
                
                success2 = int(sim_dataset[i+1, j, k])
                fail2 = int(tps_array[i+1, j]) - success2
            
                if success1 not in gamma_list:
                 
                    for m in range(0, 2):
                    
                        gamma_vect[m][p] = <float *>malloc(gamma_nsim*sizeof(float))
                        gamma_view = np.random.gamma(success1+1,size=gamma_nsim)
                        for q in xrange(0, gamma_nsim):
                        
                            gamma_vect[m][success1][q] = gamma_view[q]
                    gamma_list.append(success1)
                
                if fail1 not in gamma_list:
                
                    for m in range(0, 2):
                        
                        gamma_vect[m][p] = <float *>malloc(gamma_nsim*sizeof(float))
                        gamma_view = np.random.gamma(fail1+1,size=gamma_nsim)
                        for q in xrange(0, gamma_nsim):
                            
                            gamma_vect[1][fail1][q] = gamma_view[q]
                    gamma_list.append(fail1)
                
                
                if success2 not in gamma_list:
                    
                    for m in range(0, 2):
                        gamma_vect[m][p] = <float *>malloc(gamma_nsim*sizeof(float))
                        gamma_view = np.random.gamma(success2+1,size=gamma_nsim)
                        for q in xrange(0, gamma_nsim):
                            
                            gamma_vect[m][success2][q] = gamma_view[q]
                            
                    gamma_list.append(success2)
                
                if fail2 not in gamma_list:
                    
                    for m in range(0, 2):
                        gamma_vect[m][p] = <float *>malloc(gamma_nsim*sizeof(float))
                        gamma_view = np.random.gamma(fail2+1,size=gamma_nsim)
                        for q in xrange(0, gamma_nsim):
                            
                            gamma_vect[1][fail2][q] = gamma_view[q]
                            
                    gamma_list.append(fail2)
                    
                if interim_dict.has_key((success1, success2, fail1, fail2)):
                    
                    interim_crit[i, j, k] = interim_dict[(success1, success2, fail1, fail2)]
                else:
                    
                    sum = 0
                    for l in xrange(0, gamma_nsim):
                        sum += CriticalValue.check(gamma_vect[index0][success1][l], gamma_vect[index1][fail1][l],
                                                    gamma_vect[index1][success2][l], gamma_vect[index0][fail2][l], clin_sig)
                    interim_dict[(success1, success2, fail1, fail2)] = sum/gamma_nsim
                    interim_crit[i, j, k] = interim_dict[(success1, success2, fail1, fail2)]
                    
                    
                    
                    
    # calculate conditional power
    # calculate predictive probability
    
    if pred_flag == 1:
        
        sys.stdout.write("Calculate posterior predictive probability...")
        critical_dataset["success"] = critical_dataset["critical"] > pred_success
        # new_crit_975 = critcreate(crit_dataset, total_ps)
        """
        out_dict = {}
        for i in range(0, int(total_ps[0])):
            crit_mat0 = crit.loc[i: i+pred_num].swaplevel(0, 1).sortlevel(0)
            for j in range(0, int(total_ps[1])):
                crit_mat = crit_mat0.loc[j: j+pred_num]
                out_dict[(i, j)] = crit_mat
        return out_dict
        """
        
        
        # each_stop = futile*-1 + efficacy
        obs0 = sim_dataset[0, 2, :]
        obsa = sim_dataset[1:, 2, :]
         
        for ci in range(0, n_arm-1):
            
            for cj in xrange(0, nsim) 
         
         
         
        cp_mat0 = np.arange(0, pred_num + 1)
        cp_mata = np.arange(0, pred_num + 1)
        comb_array = comb(pred_num, cp_mata)
        for i in xrange(0, nsim):
            obs0 = int(obs0_mat[i])
            cp_obs0 = comb(predict, cp_mat0)*(beta(1+cp_mat0+obs0, predict+1+total_ps[0]-cp_mat0-obs0)/beta(1+obs0, 1+total_ps[0]-obs0))
            for j in range(0, group-1):
                obsa = int(obsa_mat[j, i])
                crit_mat = crit[(obs0, obsa)]
                cp_obsa = comb_array*(beta(1+cp_mata+obsa, predict+1+total_ps[1]-cp_mata-obsa)/beta(1+obsa, 1+total_ps[1]-obsa))
                cp_obs = np.repeat(cp_obsa, predict+1)*np.tile(cp_obs0, predict+1)
                cpower[j, i] = np.sum(cp_obs*crit_mat)
    
    
    # this could optimization
    sys.stdout.write("Summarize results...")
    
    futile = interim_crit < ful
    efficacy = interim_crit > eff
    each_stop = np.logical_or(ful, eff)
    stop = np.all(each_stop, axis=0)
    
    # calculate conditional futile, efficacy, and stop for each time
    con_futile = np.cumsum(futile, axis=1, dtype=bool)
    con_efficacy = np.cumsum(efficacy, axis=1, dtype=bool)
    con_power = np.sum(cpower, axis=1, dtype=np.float64)/nsim*100  
    
    del interim_dict, interim_crit
    
    for m in range(0, 2):
        for p in gamma_list:
            free(gamma_vect[m][p])
        free(gamma_vect[m]) 
    free(gamma_vect)
    
    clear(gamma_list)
    
    return futile, efficacy, each_stop, stop, cpower


# function to calculate conditional power

"""
def cpower(nsim, group, obs0_mat, obsa_mat, crit, total_ps):

    cpower_array = np.empty([group-1, nsim])
    cp_mat0 = np.arange(0, 451)
    cp_mata = np.arange(0, 451)
    for i in xrange(0, nsim):
        obs0 = int(obs0_mat[i])
        cp_obs0 = comb(450, cp_mat0)*(beta(1+cp_mat0+obs0, 450+1+total_ps[0]-cp_mat0-obs0)/beta(1+obs0, 1+total_ps[0]-obs0))
        for j in range(0, group-1):
            obsa = int(obsa_mat[j, i])
            crit_mat = crit[(obs0, obsa)]
            cp_obsa = comb(450, cp_mata)*(beta(1+cp_mata+obsa, 450+1+total_ps[1]-cp_mata-obsa)/beta(1+obsa, 1+total_ps[1]-obsa))
            cp_obs = np.repeat(cp_obsa, 451)*np.tile(cp_obs0, 451)
            cpower_array[j, i] = np.sum(cp_obs*crit_mat)
    cp_mean = np.sum(cpower_array, axis=1, dtype=np.float64)/nsim*100
    del cpower_array    # delete array after calculating
    return cp_mean
"""

cdef cpower(int nsim, int group, int obs0_mat, int obsa_mat, float crit, np.ndarray[DTYPE_t, ndim = 3] total_ps, int pred_num):

    cpower_array = np.empty([group-1, nsim])
    cp_mat0 = np.arange(0, pred_num + 1)
    cp_mata = np.arange(0, pred_num + 1)
    comb_array = comb(pred_num, cp_mata)
    for i in xrange(0, nsim):
        obs0 = int(obs0_mat[i])
        cp_obs0 = comb(predict, cp_mat0)*(beta(1+cp_mat0+obs0, predict+1+total_ps[0]-cp_mat0-obs0)/beta(1+obs0, 1+total_ps[0]-obs0))
        for j in range(0, group-1):
            obsa = int(obsa_mat[j, i])
            crit_mat = crit[(obs0, obsa)]
            cp_obsa = comb_array*(beta(1+cp_mata+obsa, predict+1+total_ps[1]-cp_mata-obsa)/beta(1+obsa, 1+total_ps[1]-obsa))
            cp_obs = np.repeat(cp_obsa, predict+1)*np.tile(cp_obs0, predict+1)
            cpower_array[j, i] = np.sum(cp_obs*crit_mat)
    cp_mean = np.sum(cpower_array, axis=1, dtype=np.float64)/nsim*100
    del cpower_array    # delete array after calculating
    return cp_mean

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
        if len(kwarg) == 4:
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
        elif load_file_flag == -1:
            sys.stdout.write("Generate the critical value look up table...")
            critical_dataset = CVL.output(seed, num1, num2, clin_sig, CVLfile)
        else:
            sys.stdout.write("Generate the critical value look up table...")
            critical_dataset = CVL.output(seed, num1, num2, clin_sig, ".")

    
    # cumulative sum of patients by stage
    cum_ps = np.cumsum(ps_array, axis=1)
    
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
    
    futile, efficacy, each_stop, stop = trial_progress(nsim, n_arm, n_stage, ps_array, ful, eff, clin_sig,
                                                       sim_dataset, pred_flag)
     
    
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
        con_futile_mean = np.sum(con_futile[:, i, :], axis=1, dtype=np.float64)/nsim*100
        con_efficacy_mean = np.sum(con_efficacy[:, i, :], axis=1, dtype=np.float64)/nsim*100
        con_continuous = 100 - con_efficacy_mean - con_futile_mean
        output_dict[name_stage[i]] = np.concatenate([group_mean, con_futile_mean, con_efficacy_mean, con_continuous,
                                                     cp_mean])
    df = pd.DataFrame(output_dict).transpose()
    del gamma_vect
    """
    return
