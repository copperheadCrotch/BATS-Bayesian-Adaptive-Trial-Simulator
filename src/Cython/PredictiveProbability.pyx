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
import CreateCriticalValueTable as CreateCriticalValueTable


DTYPE = np.float64
ctypedef np.float64_t DTYPE_t


# Bisection search method
@cython.boundscheck(False)
@cython.wraparound(False)
@cython.cdivision(True)
cdef Bisection(float[:, :, ::1] gamma_vect, int nsim, int n1, int n2, float predSuccess, float clinSig, int [::1] critical_array):

    # Index
    cdef Py_ssize_t i, j, k
    cdef int bisect_nsim = 500
    cdef int index0 = 0, index1 = 1
    cdef int bisect_stop = 1, mid_n, min_n, max_n, o_n
    # Critical value
    cdef float crit_arr, crit_sum

    # Assume allocation between treatment is equal
    # N1 Treatment
    # N2 Control
    sys.stdout.write("Calculate critical values...")
    for i in xrange(0, n1 + 1):
        # Initialize for the bisection search
        # To find the value meet the successful boundary
        max_n = n2
        min_n = 0
        # Get the integer
        mid_n = np.rint(max_n/2)
        while max_n > min_n:
             
            crit_sum = 0.0
            # Quick search
            for k in range(0, bisect_nsim):
            
                crit_sum += CriticalValueCal(gamma_vect[index0, i, k], gamma_vect[index1, n1-i, k], gamma_vect[index1, mid_n, k], gamma_vect[index0, n2-mid_n, k], clinSig)
            
            crit_arr = crit_sum/bisect_nsim
            # Bisection search
            if crit_arr < predSuccess:
            
                max_n = mid_n - 1
                mid_n = np.rint((max_n + min_n)/2)
            
            elif crit_arr > predSuccess:
            
                min_n = mid_n + 1
                mid_n = np.rint((min_n + max_n)/2)
            
            elif crit_arr == predSuccess:
            
                min_n = mid_n
                max_n = min_n
        
        # Exact verification
        while bisect_stop:
            
            crit_sum = 0
            for k in xrange(0, nsim):
            
                crit_sum += CriticalValueCal(gamma_vect[index0, i, k], gamma_vect[index1, n1-i, k], gamma_vect[index1, min_n, k], gamma_vect[index0, n2-min_n, k], clinSig)
            
            crit_arr = crit_sum/nsim
            
            if crit_arr > predSuccess:
            
                if o_n == -1:
                
                    bisect_stop = 0
                
                else:
                
                    min_n = min_n + 1
                    o_n = 1
                    
            elif crit_arr < predSuccess:
                
                if o_n == 1:
                
                    min_n = min_n - 1
                    bisect_stop = 0
                
                else:
                
                    min_n = min_n - 1
                    o_n = -1
                    
            elif crit_arr == predSuccess:
               
                min_n = min_n + 1
                bisect_stop = 0
        
        critical_array[i] = min_n


# For predictive probability
@cython.boundscheck(False)
@cython.wraparound(False)
@cython.cdivision(True)
cdef CalPredictiveProbability(int nsim, int nArm, int nStage, float predSuccess, float predClinSig, 
                          int searchMethod, int loadCVL, str CVLfile, int treatment_add, int control_add, 
                          int [:, :, ::1] sim_dataset, int [:, ::1] tps_array, int gamma_nsim, float [:, :, ::1] gamma_vect, 
                          double [:, ::1] cpower_array, str pathdir, list effColHeader, list patColHeader):
    
    cdef Py_ssize_t ci, cj, ck, cl, cm, cn, cp, co, cq, cs
    cdef int beta_index1, beta_index2, beta_index3, beta_index4
    # Obs_succ_control, trt: observed data
    # Pred_trt_add, control_add: patients added
    # Pred_trt, pred_control: pred_data + observed_data
    cdef int obs_succ_control, obs_succ_treatment, predict_nSuccess
    # New patients added
    # Total patients 
    cdef int predict_treatment, predict_control
    predict_treatment = treatment_add + tps_array[0, nStage - 1]
    predict_control = control_add + tps_array[nArm - 1, nStage - 1]
    cdef int index_treatment, index_control, cl_copy, cm_copy, cq_copy
    cdef float cpower_sum
    # Total index
    cdef dict pred_control_dict = {}
    cdef dict pred_treatment_dict = {}
    cdef dict pred_total_dict = {}
    # Critical value for bisection search methods
    cdef int *critical_array_pointer = <int *>malloc((predict_treatment + 1) * sizeof(int))
    cdef int [::1] critical_array = <int[:(predict_treatment + 1)]> critical_array_pointer
    # Treatment 
    cdef float *probBetaBinomial_treatment_pointer = <float *>malloc((treatment_add + 1) * nsim * sizeof(float))
    cdef float [:, ::1] probBetaBinomial_treatment = <float[:(treatment_add + 1), :nsim]> probBetaBinomial_treatment_pointer
    # Control
    cdef float *probBetaBinomial_control_pointer = <float *>malloc((control_add + 1) * nsim * sizeof(float))
    cdef float [:, ::1] probBetaBinomial_control = <float[:(control_add + 1), :nsim]> probBetaBinomial_control_pointer
    
    predClinSig = np.around(predClinSig, decimals = 3)
    # Calculate posterior predictive probability        
    if searchMethod == 2:
            
        if loadCVL == 1:
                
            sys.stdout.write("Read critical value look up table...")
            try:
                  
                critical_dataset = pd.read_csv(CVLfile, index_col = [0, 1])
                pd_index = critical_dataset.columns.values[0]
                if np.around(float(pd_index), decimals = 3) == np.around(predClinSig, decimals = 3) and max(critical_dataset.index.levels[0]) == predict_treatment and max(critical_dataset.index.levels[1]) == predict_control: 
                
                    critical_dataset["success"] = critical_dataset[pd_index] > predSuccess
                    del critical_dataset[pd_index]
                
                else:
                    
                    sys.stdout.write("Oops! Fail to load the correct critical value look up table...")
                    del critical_dataset
                    return
                
            except:
                    
                sys.stdout.write("Oops! Fail to load critical value look up table...")
                return
                
        else: 
                
            sys.stdout.write("Generate critical value look-up table...")
            critical_dataset = CreateCriticalValueTable.OutputCriticalValue(gamma_vect, pathdir, predict_treatment, predict_control, predClinSig) 
            pd_index = critical_dataset.columns.values[0]
            critical_dataset['success'] = critical_dataset[pd_index] > predSuccess
            del critical_dataset[pd_index]
                
        for cn in range(0, predict_treatment + 1):
                 
            sub_critical_dataset =  critical_dataset.loc[cn][critical_dataset.loc[cn]["success"] == 1]
            if len(sub_critical_dataset) > 0:
                
                critical_array[cn] = max(sub_critical_dataset.index)
                
            else:
                    
                critical_array[cn] = 0
                    
        del critical_dataset, sub_critical_dataset
                
    else:
            
        sys.stdout.write("Using bisection search algorithm to find the pair...")
        Bisection(gamma_vect, gamma_nsim, predict_treatment, predict_control, predSuccess, predClinSig, critical_array)                
    
    # Write out the critical array file     
    sys.stdout.write("Calculate Beta-Binomial probabilities for control...")             
    # Control arm
    for cl in xrange(0, control_add + 1):
            
        for ck in xrange(0, nsim):
            
            # Observed success in the control at the final stage of Phase II
            obs_succ_control = sim_dataset[nArm - 1, nStage - 1, ck]
                
            if obs_succ_control in pred_control_dict:
                
                cl_copy = pred_control_dict[obs_succ_control]
                probBetaBinomial_control[cl, ck] = probBetaBinomial_control[cl, cl_copy]
                
            else:
                
                # Create element for choose function
                predict_nSuccess = cl + obs_succ_control
                beta_index1 = predict_nSuccess
                beta_index2 = cl
                beta_index3 = tps_array[nArm - 1, nStage - 1] + control_add - predict_nSuccess
                beta_index4 = control_add - cl
                # Calculate beta binomial probability
                probBetaBinomial_control[cl, ck] =  gsl_sf_choose(beta_index1, beta_index2) * gsl_sf_choose(beta_index3, beta_index4)/gsl_sf_choose(predict_control + 1 , control_add)
                pred_control_dict[obs_succ_control] = ck
           
        pred_control_dict.clear()
        
    del pred_control_dict   
         
    sys.stdout.write("Calculate Beta-Binomial probabilities for treatment...")  
       
    # Treatment arm
    for ci in range(0, nArm - 1):
            
        for cj in xrange(0, nsim):
            
            obs_succ_treatment = sim_dataset[ci, nStage - 1, cj]
            obs_succ_control = sim_dataset[nArm - 1, nStage - 1, cj]
                
            if obs_succ_treatment in pred_treatment_dict:
                
                cm_copy = pred_treatment_dict[obs_succ_treatment]
                    
                for cp in xrange(0, treatment_add + 1):
                        
                    probBetaBinomial_treatment[cp, cj] = probBetaBinomial_treatment[cp, cm_copy]
                
            else:
                # Simulated success for the added patients
                for cm in xrange(0, treatment_add + 1):
                
                    predict_nSuccess = cm + obs_succ_treatment
                    beta_index1 = predict_nSuccess
                    beta_index2 = cm
                    beta_index3 = tps_array[ci, nStage - 1] + treatment_add - predict_nSuccess
                    beta_index4 = treatment_add - cm
                    # Calculate beta binomial probability
                    probBetaBinomial_treatment[cm, cj] =  gsl_sf_choose(beta_index1, beta_index2) * gsl_sf_choose(beta_index3, beta_index4)/gsl_sf_choose(predict_treatment + 1 , treatment_add)
                                            
                pred_treatment_dict[obs_succ_treatment] = cj
                
            pred_treatment_dict.clear()
                                
            if (obs_succ_control, obs_succ_treatment) in pred_total_dict:
                
                cpower_array[ci, cj] = pred_total_dict[(obs_succ_control, obs_succ_treatment)]
                
            else:
                        
                cpower_sum = 0

                for cq in xrange(0, treatment_add + 1):                      
                          
                    index_treatment = cq + obs_succ_treatment 
                    cq_copy = critical_array[index_treatment] - obs_succ_control
                            
                    if cq_copy < 0:
                            
                        cq_copy = 0
                            
                    elif cq_copy > control_add:
                            
                        cq_copy = control_add + 1
                            
                    for cl in xrange(0, cq_copy):
                            
                        cpower_sum += probBetaBinomial_control[cl, cj] * probBetaBinomial_treatment[cq, cj]
                            
                cpower_array[ci, cj] = cpower_sum     
                pred_total_dict[(obs_succ_control, obs_succ_treatment)] = cpower_array[ci, cj]
    
    predict_df_index = range(1, nsim + 1)
    sys.stdout.write("Output predictive probabilities data...")
    os.makedirs(pathdir + "Predictive Probability")
    cpower_array_copy = np.transpose(np.asarray(cpower_array), (1, 0))
    cpower_df = pd.DataFrame(cpower_array_copy, index=predict_df_index, columns=effColHeader[0:(nArm - 1)]).sort_index()
    cpower_df.index.name = "# of Simulation"
    cpower_df.to_csv(pathdir + "Predictive Probability/Predictive Probabilities.csv")
    sys.stdout.write("Output plot for predictive probabilities...")   
    
    color_map = [(31, 119, 180), (174, 199, 232), (255, 127, 14), (255, 187, 120),    
             (44, 160, 44), (152, 223, 138), (214, 39, 40), (255, 152, 150),    
             (148, 103, 189), (197, 176, 213), (140, 86, 75), (196, 156, 148),    
             (227, 119, 194), (247, 182, 210), (127, 127, 127), (199, 199, 199),    
             (188, 189, 34), (219, 219, 141), (23, 190, 207), (158, 218, 229)] 
        
    color = random.sample(color_map, 1)
    r, g, b = color[0]
    color[0] = (r/255., g/255., b/255.)   
    """
    plt.figure(figsize = (5.0, 5.0))
    
    x = np.arange(0, predict_treatment + 1)
    y = np.asarray(critical_array)
    plt.plot(x, y, color = color[0], linewidth=2.0, linestyle="-")
    plt.fill_between(x, 0, y, facecolor= color[0], interpolate=True)
    plt.tick_params(axis='both', which='major', labelsize=15)
    plt.tick_params(axis='both', which='minor', labelsize=15)             
    plt.xlabel("Number of Successes in Treatment", fontsize = 15)
    plt.ylabel("Maximum Number of Successes in Control", fontsize = 15)
    plt.xlim((0, predict_treatment))
    plt.ylim((0, predict_control))

    plt.suptitle("Successful Pairs", fontsize = 20)
    plt.tight_layout()
    plt.savefig(pathdir + "Predictive Probability/Successful Pairs.png")
    plt.close()
    """
    free(critical_array_pointer)
    del pred_treatment_dict, pred_total_dict
    
    return 1    


# For predictive probability
@cython.boundscheck(False)
@cython.wraparound(False)
@cython.cdivision(True)
cdef CalAdaPredictiveProbability(int nsim, int nArm, int nStage, float predSuccess, float predClinSig, 
                          int searchMethod, int loadCVL, str CVLfile, int treatment_add, int control_add, 
                          int [:, :, ::1] sim_dataset, int [:, ::1] tps_array, int gamma_nsim, float [:, :, ::1] gamma_vect, 
                          double [:, ::1] cpower_array, str pathdir, list effColHeader, list patColHeader):
    
    cdef Py_ssize_t ci, cj, ck, cl, cm, cn, cp, co, cq, cs
    cdef int beta_index1, beta_index2, beta_index3, beta_index4
    # Obs_succ_control, trt: observed data
    # Pred_trt_add, control_add: patients added
    # Pred_trt, pred_control: pred_data + observed_data
    cdef int obs_succ_control, obs_succ_treatment, predict_nSuccess
    # New patients added
    # Total patients 
    cdef int predict_treatment, predict_control
    predict_treatment = treatment_add + tps_array[0, nStage - 1]
    predict_control = control_add + tps_array[nArm - 1, nStage - 1]
    cdef int index_treatment, index_control, cl_copy, cm_copy, cq_copy
    cdef float cpower_sum
    # Total index
    cdef dict pred_control_dict = {}
    cdef dict pred_treatment_dict = {}
    cdef dict pred_total_dict = {}
    # Critical value for bisection search methods
    cdef int *critical_array_pointer = <int *>malloc((predict_treatment + 1) * sizeof(int))
    cdef int [::1] critical_array = <int[:(predict_treatment + 1)]> critical_array_pointer
    # Treatment 
    cdef float *probBetaBinomial_treatment_pointer = <float *>malloc((treatment_add + 1) * nsim * sizeof(float))
    cdef float [:, ::1] probBetaBinomial_treatment = <float[:(treatment_add + 1), :nsim]> probBetaBinomial_treatment_pointer
    # Control
    cdef float *probBetaBinomial_control_pointer = <float *>malloc((control_add + 1) * nsim * sizeof(float))
    cdef float [:, ::1] probBetaBinomial_control = <float[:(control_add + 1), :nsim]> probBetaBinomial_control_pointer
    
    predClinSig = np.around(predClinSig, decimals = 3)
    # Calculate posterior predictive probability            
    # Write out the critical array file     
    sys.stdout.write("Calculate Beta-Binomial probabilities for control...")             
    # Control arm
    for cl in xrange(0, control_add + 1):
            
        for ck in xrange(0, nsim):
            
            # Observed success in the control at the final stage of Phase II
            obs_succ_control = sim_dataset[nArm - 1, nStage - 1, ck]
                
            if obs_succ_control in pred_control_dict:
                
                cl_copy = pred_control_dict[obs_succ_control]
                probBetaBinomial_control[cl, ck] = probBetaBinomial_control[cl, cl_copy]
                
            else:
                
                # Create element for choose function
                predict_nSuccess = cl + obs_succ_control
                beta_index1 = predict_nSuccess
                beta_index2 = cl
                beta_index3 = tps_array[nArm - 1, nStage - 1] + control_add - predict_nSuccess
                beta_index4 = control_add - cl
                # Calculate beta binomial probability
                probBetaBinomial_control[cl, ck] =  gsl_sf_choose(beta_index1, beta_index2) * gsl_sf_choose(beta_index3, beta_index4)/gsl_sf_choose(predict_control + 1 , control_add)
                pred_control_dict[obs_succ_control] = ck
           
        pred_control_dict.clear()
        
    del pred_control_dict   
         
    sys.stdout.write("Calculate Beta-Binomial probabilities for treatment...")  
       
    # Treatment arm
    for ci in range(0, nArm - 1):
            
        for cj in xrange(0, nsim):
            
            obs_succ_treatment = sim_dataset[ci, nStage - 1, cj]
            obs_succ_control = sim_dataset[nArm - 1, nStage - 1, cj]
                
            if obs_succ_treatment in pred_treatment_dict:
                
                cm_copy = pred_treatment_dict[obs_succ_treatment]
                    
                for cp in xrange(0, treatment_add + 1):
                        
                    probBetaBinomial_treatment[cp, cj] = probBetaBinomial_treatment[cp, cm_copy]
                
            else:
                # Simulated success for the added patients
                for cm in xrange(0, treatment_add + 1):
                
                    predict_nSuccess = cm + obs_succ_treatment
                    beta_index1 = predict_nSuccess
                    beta_index2 = cm
                    beta_index3 = tps_array[ci, nStage - 1] + treatment_add - predict_nSuccess
                    beta_index4 = treatment_add - cm
                    # Calculate beta binomial probability
                    probBetaBinomial_treatment[cm, cj] =  gsl_sf_choose(beta_index1, beta_index2) * gsl_sf_choose(beta_index3, beta_index4)/gsl_sf_choose(predict_treatment + 1 , treatment_add)
                                            
                pred_treatment_dict[obs_succ_treatment] = cj
                
            pred_treatment_dict.clear()
                                
            if (obs_succ_control, obs_succ_treatment) in pred_total_dict:
                
                cpower_array[ci, cj] = pred_total_dict[(obs_succ_control, obs_succ_treatment)]
                
            else:
                        
                cpower_sum = 0

                for cq in xrange(0, treatment_add + 1):                      
                          
                    index_treatment = cq + obs_succ_treatment 
                    cq_copy = critical_array[index_treatment] - obs_succ_control
                            
                    if cq_copy < 0:
                            
                        cq_copy = 0
                            
                    elif cq_copy > control_add:
                            
                        cq_copy = control_add + 1
                            
                    for cl in xrange(0, cq_copy):
                            
                        cpower_sum += probBetaBinomial_control[cl, cj] * probBetaBinomial_treatment[cq, cj]
                            
                cpower_array[ci, cj] = cpower_sum     
                pred_total_dict[(obs_succ_control, obs_succ_treatment)] = cpower_array[ci, cj]
    
    predict_df_index = range(1, nsim + 1)
    sys.stdout.write("Output predictive probabilities data...")
    cpower_array_copy = np.transpose(np.asarray(cpower_array), (1, 0))
    cpower_df = pd.DataFrame(cpower_array_copy, index=predict_df_index, columns=effColHeader[0:(nArm - 1)]).sort_index()
    cpower_df.index.name = "# of Simulation"
    cpower_df.to_csv(pathdir + "Predictive Probability/Predictive Probabilities.csv")
    sys.stdout.write("Output plot for predictive probabilities...")   
    
    """
    color_map = [(31, 119, 180), (174, 199, 232), (255, 127, 14), (255, 187, 120),    
             (44, 160, 44), (152, 223, 138), (214, 39, 40), (255, 152, 150),    
             (148, 103, 189), (197, 176, 213), (140, 86, 75), (196, 156, 148),    
             (227, 119, 194), (247, 182, 210), (127, 127, 127), (199, 199, 199),    
             (188, 189, 34), (219, 219, 141), (23, 190, 207), (158, 218, 229)] 
        
    color = random.sample(color_map, 1)
    r, g, b = color[0]
    color[0] = (r/255., g/255., b/255.)   
    
    plt.figure(figsize = (5.0, 5.0))
    
    x = np.arange(0, predict_treatment + 1)
    y = np.asarray(critical_array)
    plt.plot(x, y, color = color[0], linewidth=2.0, linestyle="-")
    plt.fill_between(x, 0, y, facecolor= color[0], interpolate=True)
    plt.tick_params(axis='both', which='major', labelsize=15)
    plt.tick_params(axis='both', which='minor', labelsize=15)             
    plt.xlabel("Number of Successes in Treatment", fontsize = 15)
    plt.ylabel("Maximum Number of Successes in Control", fontsize = 15)
    plt.xlim((0, predict_treatment))
    plt.ylim((0, predict_control))

    plt.suptitle("Successful Pairs", fontsize = 20)
    plt.tight_layout()
    plt.savefig(pathdir + "Predictive Probability/Successful Pairs.png")
    plt.close()
    """
    free(critical_array_pointer)
    del pred_treatment_dict, pred_total_dict
    return 1    

    

def PredictiveProbability(nsim, nArm, nStage, predSuccess, predClinSig, searchMethod, loadCVL, 
                                CVLfile, treatment_add, control_add, sim_dataset, tps_array, gamma_nsim, gamma_vect, cpower_array,
                                pathdir, effColHeader, patColHeader):
    
    return CalPredictiveProbability(nsim, nArm, nStage, predSuccess, predClinSig, searchMethod, loadCVL, 
                                CVLfile, treatment_add, control_add, sim_dataset, tps_array, gamma_nsim, gamma_vect, cpower_array,
                                pathdir, effColHeader, patColHeader)
