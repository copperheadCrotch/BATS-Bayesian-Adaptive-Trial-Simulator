# Cython module
import cython
cimport cython

# Import cython_gsl module
from cython_gsl cimport *
# Import malloc, free
from libc.stdlib cimport malloc, free

# Import C functions
from CriticalValueCal cimport CriticalValueCal

# Import other packages
import numpy as np
cimport numpy as np
import sys
import time
import pandas as pd
import FixedTrialData as TrialData
import AllocFinder as AllocFinder
import GammaGenerate as GammaGenerate
import InterimAnalysis as InterimAnalysis
import PredictiveProbability as PredictiveProbability

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
cdef TrialProgress(str pathdir, list effColHeader, list patColHeader, int nsim, int seed, int nArm, int nStage, double [::1] te_list, 
                   int [::1] ns_list, float alloc, float eff, float fut, float clinSig, 
                   int predict = 0, int predNum = 0, float predSuccess = 0, float predClinSig = 0, int searchMethod = 0, int loadCVL = 0, 
                   str CVLfile = ""):
    
    # Index
    cdef Py_ssize_t m, p, q, i, j, k, l, copy_i, copy_j, copy_k
    cdef int best_treatment, best_control
    cdef int gamma_nsim = 50000, total_index = 2
    # Variable for beta random variable generation
    cdef int max_tps, treatment_add, control_add
    # Patients at each arm, cumulative
    cdef int [:, ::1] ps_array = np.empty((nArm, nStage), dtype = np.intc)
    
    for i in range(0, len(ns_list)):
            
        best_treatment, best_control = AllocFinder.BestPatientAllocation(nArm, alloc, ns_list[i])       
        ps_array[0 : (nArm - 1), i] = best_treatment
        ps_array[(nArm - 1), i] = best_control
    
    cdef int [:, ::1] tps_array = np.cumsum(ps_array, axis=1)
    # Patients at each stage at each arm
    sys.stdout.write("\nPatients of each arm at each stage:")
    df_ps_array = pd.DataFrame(np.transpose(ps_array), index= patColHeader, columns= effColHeader)
    sys.stdout.write(df_ps_array)
    # Possible maximum number of patients
    # Add_tps: added new patients allocated to treatment
    
    if predict == 1:
        
        treatment_add, control_add = AllocFinder.BestPatientAllocation(nArm, alloc, predNum)
        patnum_string = "Number of patient:\t" + str(treatment_add) + "\t" + str(control_add)    
        sys.stdout.write("\nThe best added patients assignment: ")    
        sys.stdout.write("\tTreatment:                       \tControl:")       
        sys.stdout.write(patnum_string)
        max_tps = max(treatment_add, control_add) + max(tps_array[:, nStage - 1]) +  1
    
    else: 
        
        treatment_add = 1
        control_add = 1
        max_tps = max(tps_array[:, nStage - 1]) + 1
    
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
    con_futile_mean, con_efficacy_mean, futile_mean, efficacy_mean = InterimAnalysis.InterimCheck(nsim, nArm, 
                                 nStage, eff, fut, clinSig, sim_dataset, tps_array, 
                                 gamma_nsim, gamma_vect, pathdir, effColHeader, patColHeader)
   
    
    if predict != 1:
        
        free(gamma_array)
    
    # For predictive probability
    cdef double *cpower_array_pointer = <double *>malloc((nArm - 1) * nsim * sizeof(double))
    cdef double [:, ::1] cpower_array = <double[:(nArm - 1), :nsim]> cpower_array_pointer
    cdef np.ndarray[double, ndim = 1] con_power = np.empty((nArm - 1), dtype=np.float64)
    # cdef np.ndarray [dtype=float, ndim = 1] con_power = np.empty(n_arm-1)
    # Calculate posterior predictive probability
    if predict == 1:
        
        sys.stdout.write("Calculate posterior predictive probability...") 
        predictflag = PredictiveProbability.PredictiveProbability(nsim, nArm, nStage, predSuccess, predClinSig,  searchMethod, loadCVL, 
                                CVLfile, treatment_add, control_add, sim_dataset, tps_array, gamma_nsim, gamma_vect, cpower_array,
                                pathdir, effColHeader, patColHeader)
        free(gamma_array)
        if predictflag != 1:
            
            return 1
            
        sys.stdout.write("Generate results...")        
        con_sim_mean_copy = np.around(np.mean(sim_dataset[0:(nArm - 1), :, :], axis = 2).reshape((nArm - 1) * nStage, 1), 2)
        con_futile_mean_copy = con_futile_mean.reshape((nArm - 1) * nStage, 1)
        con_efficacy_mean_copy = con_efficacy_mean.reshape((nArm - 1)* nStage, 1)
        con_continuous_mean = 100 - con_futile_mean - con_efficacy_mean
        con_continuous_mean_copy = con_continuous_mean.reshape((nArm - 1)* nStage, 1)
        futile_mean_copy = futile_mean.reshape((nArm - 1) * nStage, 1)
        efficacy_mean_copy = efficacy_mean.reshape((nArm - 1) * nStage, 1)
        continuous_mean = 100 - futile_mean - efficacy_mean
        continuous_mean_copy = continuous_mean.reshape((nArm - 1) * nStage, 1)
        con_power_empty = np.empty(((nArm - 1), (nStage - 1)))
        con_power_empty[:] = np.NaN
        con_power = np.sum(cpower_array, axis = 1)/nsim * 100
        con_power_copy = np.concatenate((con_power_empty, con_power.reshape((nArm - 1), 1)), axis = 1).reshape((nArm - 1) * nStage, 1)
        final_copy = np.concatenate((con_sim_mean_copy, con_futile_mean_copy, con_efficacy_mean_copy, 
                                     con_continuous_mean_copy, futile_mean_copy, efficacy_mean_copy, 
                                     continuous_mean_copy, con_power_copy), axis = 1)
        final_copy = np.around(final_copy, decimals = 2)
        final_df_index = [range(1, nArm), range(1, nStage + 1)]
        resultHeader = ["Average Success", "Conditional Futility(%)", "Conditional Efficacy(%)", "Conditional Continuous(%)", 
                        "Unconditional Futility(%)", "Unconditional Efficacy(%)", "Unconditional Continuous(%)", 
                        "Predictive Probability(%)"]
        final_df = pd.DataFrame(final_copy, index=pd.MultiIndex.from_product(final_df_index, names=["Treatment Arm", "Stage"]), columns=resultHeader).sort_index()
        final_df.to_csv(pathdir + "FinalResult.csv")
        
        del con_power_empty, con_power_copy
     
    else: 
        
        sys.stdout.write("Generate results...")
        con_sim_mean_copy = np.around(np.mean(sim_dataset[0:(nArm - 1), :, :], axis = 2).reshape((nArm - 1) * nStage, 1), 2)
        con_futile_mean_copy = con_futile_mean.reshape((nArm - 1) * nStage, 1)
        con_efficacy_mean_copy = con_efficacy_mean.reshape((nArm - 1) * nStage, 1)
        con_continuous_mean = 100 - con_futile_mean - con_efficacy_mean
        con_continuous_mean_copy = con_continuous_mean.reshape((nArm - 1)* nStage, 1)
        futile_mean_copy = futile_mean.reshape((nArm - 1) * nStage, 1)
        efficacy_mean_copy = efficacy_mean.reshape((nArm - 1) * nStage, 1)
        continuous_mean = 100 - futile_mean - efficacy_mean
        continuous_mean_copy = continuous_mean.reshape((nArm - 1) * nStage, 1)
        final_copy = np.concatenate((con_sim_mean_copy, con_futile_mean_copy, con_efficacy_mean_copy, con_continuous_mean_copy, 
                                     futile_mean_copy, efficacy_mean_copy, continuous_mean_copy), axis = 1)
        final_copy = np.around(final_copy, decimals = 2)
        final_df_index = [range(1, nArm), range(1, nStage + 1)]
        resultHeader = ["Average Success", "Conditional Futility(%)", "Conditional Efficacy(%)", "Conditional Continuous(%)", 
                        "Unconditional Futility(%)", "Unconditional Efficacy(%)", "Unconditional Continuous(%)"]
        final_df = pd.DataFrame(final_copy, index=pd.MultiIndex.from_product(final_df_index, names=["Treatment Arm", "Stage"]), columns=resultHeader).sort_index()
        final_df.to_csv(pathdir + "FinalResult.csv")  
    
    del sim_dataset, con_sim_mean_copy, con_futile_mean, con_futile_mean_copy, con_efficacy_mean, con_efficacy_mean_copy, con_continuous_mean, con_continuous_mean_copy, futile_mean, futile_mean_copy, efficacy_mean, efficacy_mean_copy, continuous_mean, continuous_mean_copy, final_copy, con_power
    free(sim_dataset_pointer)
    free(cpower_array_pointer)
           
    return 0
# Trial simulation(nseed, nsim, out_dir, te_list, clinical_sig, futile_cut, efficacy_cut,
#                                     alloc, ps_array, efficacy_bound, n_group, n_stage)
# Initialize the trial simulation here
# Include trial data generation, trial progress simulation and predictive probability calculation


def TrialSimulation(pathdir, effColHeader, patColHeader, nsim, seed, nArm, nStage, te_list, ns_list, alloc, eff, fut, clinSig, predict, predNum, predSuccess, predClinSig, searchMethod, loadCVL, CVLfile):
    

    finish_flag = 0 
    if seed == 0:
        
        seed = np.random.randint(1, 12345, size=1)  
        
    if predict != 1:
        
        predNum = 0
        predSuccess = 0
        predClinSig = 0
        searchMethod = 0
        loadCVL = 0
        CVLfile = ""
        
    te_list = np.array(te_list)
    ns_list = np.array(ns_list, dtype = np.intc)
      
    start_time = time.time()  
    # inpathdir = bytes(pathdir, "utf-8")
    # inCVLfile = bytes(CVLfile, "utf-8") 
    # Get futility, efficacy, stop for each arm and stop totally
    if predict == 1:
        
        finish_flag = TrialProgress(pathdir, effColHeader, patColHeader, nsim, seed, nArm, nStage, te_list, ns_list, alloc, eff, fut, 
                                                               clinSig, predict, predNum, predSuccess, predClinSig, searchMethod, loadCVL, 
                                                               CVLfile)
    
        
    else:
        

        finish_flag = TrialProgress(pathdir, effColHeader, patColHeader, nsim, seed, nArm, nStage, te_list, ns_list, alloc, eff, fut, 
                                                               clinSig, predict, predNum, predSuccess, predClinSig, searchMethod, loadCVL, 
                                                               CVLfile)

    import gc
    gc.collect()
    
    finish_time = np.around(time.time() - start_time, 3)
    sys.stdout.write("Time used: %s secs"%str(finish_time))
        
    return finish_flag

