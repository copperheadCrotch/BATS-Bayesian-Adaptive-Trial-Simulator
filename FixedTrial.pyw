import numpy as np
import sys
import os
import pandas as pd
import re
from scipy.special import beta
from scipy.misc import comb
# import GammaGenerate as gammag
# from datetime import datetime
import CVL10 as CVL

# generate trial data
# te_list: treatment effects for each group:, [p0,p1,p2...pn]


def trial_data(nsim, n_arm, n_stage, te_list, ps_array):

    trial_array = np.empty([n_arm, n_stage, nsim])
    for i in range(n_arm):
        for j in range(n_stage):
            trial_array[i, j, :] = np.random.binomial(ps_array[i, j], te_list[i], size=nsim)
    # cumulative
    final_data = np.cumsum(trial_array, axis=1)
    print "done"
    print final_data
    del trial_array
    return final_data


# function to generate the lookup value.
# the theta_null and theta_trt are gamma random variables
# critical value is usually 0.05
# return P((theta1 - theta2)>mu)


def interim_look(g1, g2, g3, g4, critical_value):

    theta_null = g1/(g1 + g2)
    theta_trt = g3/(g3 + g4)
    crit = np.sum(theta_trt > (theta_null + critical_value), dtype=np.float64)/len(theta_null)
    return crit


# trial_progress(nsim, clinical_sig, futile_cut, efficacy_cut, sim_dataset,
#                 gamma_vect, n_group, n_stage)
# check trial progress
# use futile_cut, efficacy cut


def trial_progress(nsim, clinical_sig, futile_cut, efficacy_cut, ps_array, sim_dataset, gamma_vect, n_group, n_stage):

    interim_dict = {}
    interim_crit = np.empty([n_group-1, n_stage, nsim])
    tps_array = np.cumsum(ps_array, axis=1)
    for k in xrange(0, nsim):
        for j in range(0, n_stage):
            index1 = int(sim_dataset[0, j, k])
            total1 = int(tps_array[0, j])
            for i in range(0, n_group-1):
                index2 = int(sim_dataset[i+1, j, k])
                total2 = int(tps_array[i+1, j])
                if interim_dict.has_key((index1, index2, total1, total2)):
                    interim_crit[i, j, k] = interim_dict[(index1, index2, total1, total2)]
                else:
                    interim_dict[(index1, index2, total1, total2)] = interim_look(gamma_vect[index1, :, 0],
                                                                                  gamma_vect[total1-index1, :, 1],
                                                                                  gamma_vect[index2, :, 1],
                                                                                  gamma_vect[total2-index2, :, 0],
                                                                                  clinical_sig)
                    interim_crit[i, j, k] = interim_dict[(index1, index2, total1, total2)]
    futile = interim_crit < futile_cut
    efficacy = interim_crit > efficacy_cut
    each_stop = np.logical_or(futile, efficacy)
    stop = np.all(each_stop, axis=0)
    del interim_dict
    return futile, efficacy, each_stop, stop


# function to create critical value


def critcreate(crit, total_ps):

    out_dict = {}
    for i in range(0, int(total_ps[0])):
        crit_mat0 = crit.loc[i: i+450].swaplevel(0, 1).sortlevel(0)
        for j in range(0, int(total_ps[1])):
            crit_mat = crit_mat0.loc[j: j+450]
            out_dict[(i, j)] = crit_mat
    return out_dict


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

def cpower(nsim, group, obs0_mat, obsa_mat, crit, total_ps, predict):

    cpower_array = np.empty([group-1, nsim])
    cp_mat0 = np.arange(0, predict + 1)
    cp_mata = np.arange(0, predict + 1)
    comb_array = comb(predict, cp_mata)
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
            if CVLfile_type == "p":
                critical_dataset = pd.read_pickle(CVLfile)
            elif CVLfile_type == "csv":
                critical_dataset = pd.read_csv(CVLfile)
        elif load_file_flag == -1:
            sys.stdout.write("Generate the critical value look up table...")
            CVL.output(seed, num1, num2, clin_sig, CVLfile)
        else:
            sys.stdout.write("Generate the critical value look up table...")
            CVL.output(seed, num1, num2, clin_sig, ".")

    
    # total number of patients at each stage    
    total_ps = np.sum(ps_array, axis=1)
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
    sys.stdout.write("Calculate the futility and efficacy...")
    
    """
    # get futility, efficacy, stop for each arm and stop totally
    futile, efficacy, each_stop, stop = trial_progress(nsim, clinical_sig, ful, eff, ps_array,
                                                       sim_dataset, gamma_vect, n_group, n_stage)

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

