# Cython module
import cython
cimport cython

# Import cython_gsl module
from cython_gsl cimport *
# Import malloc, free
from libc.stdlib cimport malloc, free

# Import C functions
from BATS.CriticalValueCal cimport CriticalValueCal

# Import other packages
import numpy as np
cimport numpy as np
import sys
import pandas as pd
import matplotlib
matplotlib.use('Qt5Agg') 
import BATS.FixedTrialData as TrialData
import BATS.AllocFinder as AllocFinder
import BATS.GammaGenerate as GammaGenerate
import BATS.InterimAnalysis as InterimAnalysis
import BATS.PredictiveProbability as PredictiveProbability

DTYPE = np.float64
ctypedef np.float64_t DTYPE_t


# Check trial progress
# Return futile, efficacy
# If predictive probability is required, calculate it
# Nsim: number of simulations
# Seed: simulation seed
# N_arm: number of arms
# N_stage: number of stages
# Ps_array: patients assignment
# Fut, eff: futility and efficacy boundary
# Clin_sig: clinical significance
# Sim_dataset: simulated dataset
@cython.boundscheck(False)
@cython.wraparound(False)
@cython.cdivision(True)
cdef TrialProgress(str pathdir, list effColHeader, list patColHeader, int nsim, int seed , int nArm, int nStage, 
                   double [::1] te_list, int [::1] prior_list, int [::1] ns_list, float alloc, double [::1] eff, 
                   double [::1] fut, float clinSig, int predict, int [::1] predns_list,  float predSuccess, float predClinSig = 0):
                   
    # Index
    cdef Py_ssize_t m, p, q, i, j, k, l, copy_i, copy_j, copy_k
    cdef int best_treatment, best_control
    cdef int gamma_nsim = 50000, total_index = 2
    cdef int max_tps, treatment_add, control_add
    # Patients at each arm, cumulative
    cdef int [:, ::1] ps_array = np.empty((nArm, nStage), dtype = np.intc)
    cdef int [:, ::1] predNum = np.empty((nArm, nStage), dtype = np.intc)
    cdef int [:, ::1] prior = np.empty((nArm, 2), dtype = np.intc)
    # Patient assignment
    for i in range(0, nStage):
            
        best_treatment, best_control = AllocFinder.BestPatientAllocation(nArm, alloc, ns_list[i])       
        ps_array[0 : (nArm - 1), i] = best_treatment
        ps_array[(nArm - 1), i] = best_control
    
    # Prior assignment
    for i in range(0, nArm):
            
        prior[i, 0] = prior_list[2 * i]   
        prior[i, 1] = prior_list[2 * i + 1]
        
    # Cumulative number of patients by stage
    cdef int [:, ::1] tps_array = np.cumsum(ps_array, axis=1)    
    # Patients at each stage at each arm
    sys.stdout.write("\nPatients of each arm at each stage:")
    # Print out the number of patients array
    df_ps_array = pd.DataFrame(np.transpose(ps_array), index= patColHeader, columns= effColHeader)
    # sys.stdout.write(df_ps_array)
    sys.stdout.write(df_ps_array)
    if predict == 1:
        
        for i in range(0, nStage):
            
            if predns_list[i] == 0:
                
                predNum[0: nArm, i] = 0
            
            else:
                
                treatment_add, control_add = AllocFinder.BestPatientAllocation(nArm, alloc, predns_list[i])
                predNum[0: (nArm - 1), i] = treatment_add
                predNum[(nArm - 1), i] = control_add
                if treatment_add < 1 or control_add < 1:
                    
                    sys.stdout.write("Oops, the number of added patients at stage %d is too small, no patient will be assigned to one of the arm!"%(i + 1))
                    return 1
                
                
        patnum_string = "Number of patient added:\t"    
        df_predNum = pd.DataFrame(np.transpose(predNum), index= patColHeader, columns= effColHeader)
        # sys.stdout.write(df_ps_array)
        sys.stdout.write(df_predNum)
        max_tps = max(tps_array[:, nStage - 1]) + np.amax(predNum) + np.amax(prior)
    
    else: 

        for i in range(0, nStage):
                  
            predNum[0: nArm, i] = 0
                        
        treatment_add = 1
        control_add = 1
        
        max_tps = max(tps_array[:, nStage - 1]) + np.amax(prior)
        
    # Simulated dataset  
    cdef int *sim_dataset_pointer = <int *>malloc(nArm * nStage * nsim * sizeof(int))
    cdef int [:, :, ::1] sim_dataset = <int[:nArm, :nStage, :nsim]> sim_dataset_pointer
    # Gamma array pointer
    cdef float *gamma_array = <float *>malloc(total_index * max_tps * gamma_nsim * sizeof(float))
    cdef float[:, :, ::1] gamma_vect = <float[:total_index, :max_tps, :gamma_nsim]> gamma_array
    # Generate Trial data
    TrialData.FixedTrialData(nsim, seed, nArm, nStage, te_list, ps_array, sim_dataset, pathdir, effColHeader)
    # Generate Gamma RandomVariable
    GammaGenerate.RVGamma(seed, max_tps, gamma_nsim, gamma_vect)
    # Interim Analysis
    interim_mean, con_futile_mean, con_efficacy_mean, futile_mean, efficacy_mean = InterimAnalysis.InterimPredCheck(nsim, nArm, 
                                 nStage, prior, eff, fut, clinSig, sim_dataset, tps_array, predNum, predSuccess,
                                 gamma_nsim, gamma_vect, pathdir, effColHeader, patColHeader)
   

    free(gamma_array)
    try:
         
        sys.stdout.write("Generate results...")
        ps_array_copy = np.array(ps_array).reshape((nArm * nStage), 1)
        con_sim_mean_copy = np.mean(sim_dataset[:, :, :], axis = 2).reshape((nArm * nStage), 1)
        interim_mean_copy = np.concatenate((interim_mean.reshape((nArm - 1), nStage), np.repeat(np.NaN, nStage).reshape(1, nStage)), axis = 0).reshape((nArm * nStage), 1)
        con_futile_mean_copy = np.concatenate((con_futile_mean.reshape((nArm - 1), nStage), np.repeat(np.NaN, nStage).reshape(1, nStage)), axis = 0).reshape((nArm * nStage), 1)
        con_efficacy_mean_copy = np.concatenate((con_efficacy_mean.reshape((nArm - 1), nStage), np.repeat(np.NaN, nStage).reshape(1, nStage)), axis = 0).reshape((nArm * nStage), 1)
        con_continuous_mean = 100 - con_futile_mean - con_efficacy_mean
        con_continuous_mean_copy = np.concatenate((con_continuous_mean.reshape((nArm - 1), nStage), np.repeat(np.NaN, nStage).reshape(1, nStage)), axis = 0).reshape((nArm * nStage), 1)
        futile_mean_copy = np.concatenate((futile_mean.reshape((nArm - 1), nStage), np.repeat(np.NaN, nStage).reshape(1, nStage)), axis = 0).reshape((nArm * nStage), 1)
        efficacy_mean_copy = np.concatenate((efficacy_mean.reshape((nArm - 1), nStage), np.repeat(np.NaN, nStage).reshape(1, nStage)), axis = 0).reshape((nArm * nStage), 1)
        continuous_mean = 100 - futile_mean - efficacy_mean
        continuous_mean_copy = np.concatenate((continuous_mean.reshape((nArm - 1), nStage), np.repeat(np.NaN, nStage).reshape(1, nStage)), axis = 0).reshape((nArm * nStage), 1)
        if predict != 1:
            
            final_copy = np.concatenate((ps_array_copy, con_sim_mean_copy, interim_mean_copy, con_futile_mean_copy, con_efficacy_mean_copy, con_continuous_mean_copy, 
                                     futile_mean_copy, efficacy_mean_copy, continuous_mean_copy), axis = 1)
            final_copy = np.around(final_copy, decimals = 2)
            resultHeader = ["Patient Assignment", "Average Success", "Posterior Probability", "Conditional Futility", "Conditional Efficacy", "Conditional Continuous", 
                    "Unconditional Futility", "Unconditional Efficacy", "Unconditional Continuous"]
        
        
        else:
            
            # New added patients
            predNum_copy = np.array(predNum).reshape((nArm * nStage), 1)
            posteriorprob_copy = np.empty((nArm, nStage))
            posteriorprob_copy[:] = np.NaN
            predictprob_copy = np.empty((nArm, nStage))
            predictprob_copy[:] = np.NaN
            # Split the posterior and predictive probability
            for i in range(0, nStage):
                
                # Posterior 
                if predNum[nArm - 1, i] == 0:
                    
                    posteriorprob_copy[0 : (nArm - 1), i] = interim_mean.reshape((nArm - 1), nStage)[0 : (nArm - 1), i]                      
                    
                # Predictive probability
                else:
                    
                    predictprob_copy[0 : (nArm - 1), i] = interim_mean.reshape((nArm - 1), nStage)[0 : (nArm - 1), i]   
            
            posteriorprob_copy = posteriorprob_copy.reshape((nArm * nStage), 1)
            predictprob_copy = predictprob_copy.reshape((nArm * nStage), 1)
            final_copy = np.concatenate((ps_array_copy, predNum_copy, con_sim_mean_copy, posteriorprob_copy, predictprob_copy, con_futile_mean_copy, con_efficacy_mean_copy, con_continuous_mean_copy, 
                                     futile_mean_copy, efficacy_mean_copy, continuous_mean_copy), axis = 1)
            final_copy = np.around(final_copy, decimals = 2)
            resultHeader = ["Patient Assignment", "New Patients Added", "Average Success", "Posterior Probability", "Predictive Probability", "Conditional Futility", "Conditional Efficacy", "Conditional Continuous", 
                    "Unconditional Futility", "Unconditional Efficacy", "Unconditional Continuous"]  
        
        final_df_index = [effColHeader, patColHeader]
        final_df = pd.DataFrame(final_copy, index=pd.MultiIndex.from_product(final_df_index, names=["Treatment Arm", "Stage"]), columns=resultHeader).sort_index()
        final_df.to_csv(pathdir + "FinalResult.csv")    
    
    except:
        
        sys.stdout.write("Oops, results generation failed")
        return 1
        
    del sim_dataset, con_sim_mean_copy, con_futile_mean, con_futile_mean_copy, con_efficacy_mean, con_efficacy_mean_copy, con_continuous_mean, con_continuous_mean_copy, futile_mean, futile_mean_copy, efficacy_mean, efficacy_mean_copy, continuous_mean, continuous_mean_copy, final_copy
    free(sim_dataset_pointer)
    
    return 0

# Trial simulation(nseed, nsim, out_dir, te_list, clinical_sig, futile_cut, efficacy_cut,
#                                     alloc, ps_array, efficacy_bound, n_group, n_stage)
# Initialize the trial simulation here
# Include trial data generation, trial progress simulation and predictive probability calculation


def TrialSimulation(pathdir = "./", effColHeader = [], patColHeader = [], nsim = 10000, seed = 12345, 
                    nArm = 0, nStage = 0, te_list = [], prior_list = [], ns_list = [], alloc = 1, 
                    eff_list = [], fut_list = [], clinSig = 0, predict = 0, predns_list = [], 
                    predSuccess = 0.975, predClinSig = 0.05):
    
    finish_flag = 0 
    
    if predict != 1:
        
        predns_list = []
        predSuccess = 0
        predClinSig = 0
    
    te_list = np.array(te_list)
    prior_list = np.array(prior_list,  dtype = np.intc)
    ns_list = np.array(ns_list, dtype = np.intc)
    eff_list = np.array(eff_list)
    fut_list = np.array(fut_list)
    predns_list = np.array(predns_list, dtype = np.intc)
    # Get futility, efficacy, stop for each arm and stop totally

    finish_flag = TrialProgress(pathdir, effColHeader, patColHeader, nsim, seed, nArm, nStage, te_list, prior_list, ns_list, alloc, 
                                eff_list, fut_list, clinSig, predict, predns_list, predSuccess, predClinSig)
    
    import gc
    gc.collect()
    
    return finish_flag


    