import cython
cimport cython

# Import C function
from CriticalValueCal cimport CriticalValueCal
from libc.stdlib cimport malloc, free

# Import python modules
import numpy as np
cimport numpy as np
import sys
import os
import random
import pandas as pd
import PredictiveProbability as PredictiveProbability
import matplotlib.pyplot as plt

DTYPE = np.float64
ctypedef np.float64_t DTYPE_t


# Cython function for interim analysis based on posterior predictive probability
@cython.boundscheck(False)
@cython.wraparound(False)
@cython.cdivision(True)
cdef FixedInterimPredCheck(int nsim, int nArm, int nStage, int [:, ::1] prior, double [::1] eff, double [::1] fut, float clinSig,
                  int [:, :, ::1] sim_dataset, int [:, ::1] tps_array, int [:, ::1] predNum, float predSuccess,
                  int gamma_nsim, float [:, :, ::1] gamma_vect, str pathdir, list effColHeader,
                  list patColHeader):
    
    # Define variables
    # Index used in loops
    cdef Py_ssize_t i, j, k, m, p, plot_i              
    # Number of success in the treatment/control, number of failures in the treatment/control
    cdef int succ_treatment, succ_control, fail_treatment, fail_control, control_add
    cdef int [::1] treatment_add = np.array([1] * (nArm - 1)) 
    # Variable for beta random variable generation
    cdef float gamma1, gamma2, gamma3, gamma4, gamma_sum
    cdef int index0 = 0, index1 = 1, total_index = 2
    # Interim futility/efficacy
    cdef list fut_list, eff_list, con_fut_list, con_eff_list
    # Interim dictionary to store interim posterior probability
    cdef dict interim_dict = {}
    cdef float * interim_crit_pointer = < float *> malloc((nArm - 1) * nStage * nsim * sizeof(float))
    cdef float [:, :, ::1] interim_crit = < float [:(nArm - 1), :nStage, :nsim] > interim_crit_pointer 
    cdef int * futile_pointer = < int *> malloc((nArm - 1) * nStage * nsim * sizeof(int))
    cdef int [:, :, ::1] futile = < int [:(nArm - 1), :nStage, :nsim] > futile_pointer
    cdef int * efficacy_pointer = < int *> malloc((nArm - 1) * nStage * nsim * sizeof(int))
    cdef int [:, :, ::1] efficacy = < int [:(nArm - 1), :nStage, :nsim] > efficacy_pointer
    cdef int * stop_pointer = < int *> malloc((nArm - 1) * nStage * nsim * sizeof(int))
    cdef int [:, :, ::1] stop = < int [:(nArm - 1), :nStage, :nsim] > stop_pointer 
    cdef int * con_futile_pointer = < int *> malloc((nArm - 1) * nStage * nsim * sizeof(int))
    cdef int [:, :, ::1] con_futile = < int [:(nArm - 1), :nStage, :nsim] > con_futile_pointer
    cdef int * con_efficacy_pointer = < int *> malloc((nArm - 1) * nStage * nsim * sizeof(int))
    cdef int [:, :, ::1] con_efficacy = < int [:(nArm - 1), :nStage, :nsim] > con_efficacy_pointer
    cdef np.ndarray[DTYPE_t, ndim = 2] con_futile_mean = np.empty(((nArm - 1), nStage))
    cdef np.ndarray[DTYPE_t, ndim = 2] con_efficacy_mean = np.empty(((nArm - 1), nStage))
    cdef np.ndarray[DTYPE_t, ndim = 2] futile_mean = np.empty(((nArm - 1), nStage))
    cdef np.ndarray[DTYPE_t, ndim = 2] efficacy_mean = np.empty(((nArm - 1), nStage))
    
    for j in range(0, nStage):    
        
        # Patients added for predictive probability when doing interim analysis
        for i in range(0, nArm - 1):
            
            treatment_add[i] = predNum[i, j]
        
        sys.stdout.write("Simulate interim analysis for stage %d" % (j + 1))
        control_add = predNum[nArm - 1, j]
        if control_add == 0:

            for i in range(0, nArm - 1):
            
                sys.stdout.write("Calculate posterior probability for arm %d at stage %d" % (i + 1, j + 1))
                for k in xrange(0, nsim):
                    
                    # Treatment
                    succ_treatment = sim_dataset[i, j, k] + prior[i, 0] - 1
                    fail_treatment = tps_array[i, j] - succ_treatment + prior[i, 1] - 1
                    # Control
                    succ_control = sim_dataset[nArm - 1, j, k] + prior[nArm - 1, 0] - 1
                    fail_control = tps_array[nArm - 1, j] - succ_control + prior[nArm - 1, 1] - 1
                    if (succ_treatment, succ_control, fail_treatment, fail_control) in interim_dict:
                        
                        copy_i, copy_j, copy_k = interim_dict[(succ_treatment, succ_control, fail_treatment, fail_control)]
                        interim_crit[i, j, k] = interim_crit[copy_i, copy_j, copy_k]
                        futile[i, j, k] = futile[copy_i, copy_j, copy_k]
                        efficacy[i, j, k] = efficacy[copy_i, copy_j, copy_k]
                        stop[i, j, k] = stop[copy_i, copy_j, copy_k]
                    
                    else:
                        
                        gamma_sum = 0.0
                        for l in xrange(0, gamma_nsim):
                            gamma1 = gamma_vect[index0, succ_treatment, l]
                            gamma2 = gamma_vect[index1, fail_treatment, l]
                            gamma3 = gamma_vect[index1, succ_control, l]
                            gamma4 = gamma_vect[index0, fail_control, l]
                            gamma_sum += CriticalValueCal(gamma1, gamma2, gamma3, gamma4, clinSig)
                        
                        interim_dict[(succ_treatment, succ_control, fail_treatment, fail_control)] = (i, j, k)
                        # Posterior probability P((A - B) > mu)
                        interim_crit[i, j, k] = gamma_sum / gamma_nsim            
            
            interim_dict.clear()
        
        # Both of them should larger than 0    
        # If one of them is 0 and another not, an error should be thrown out in the previous module
        # But still check the condition here to make sure it is right
        elif control_add > 0 and np.amin(treatment_add) > 0: 
            
            sys.stdout.write("Simulate predictive probability for arm %d at stage %d" % (i + 1, j + 1))
            predictflag = PredictiveProbability.InterimPredictiveProbability(nsim, nArm, j, prior, predSuccess, clinSig,
                    treatment_add, control_add, sim_dataset, tps_array, gamma_nsim, gamma_vect, interim_crit,
                    pathdir, effColHeader, patColHeader)
            
            if predictflag != 1:
                
                sys.stdout.write("Oops, fail to calculate the predictive probability at stage %d"%(j + 1)) 
                return
        
        # Else: there is error, return
        else: 
            
            return
        
        
        for i in range(0, nArm - 1):   
            
            for k in xrange(0, nsim):
                
                futile[i, j, k] = interim_crit[i, j, k] < fut[j]
                # Efficacy Boundary
                efficacy[i, j, k] = interim_crit[i, j, k] >= eff[j]
                # Whether the trial is stopped
                stop[i, j, k] = futile[i, j, k] | efficacy[i, j, k]                

                if j == 0:
                    
                    con_efficacy[i, j, k] = efficacy[i, j, k]
                    con_futile[i, j, k] = futile[i, j, k]
                    
                else:
                    
                    if con_futile[i, j - 1, k] == 1:
                        
                        con_futile[i, j, k] = 1
                        con_efficacy[i, j, k] = 0
                    
                    elif con_efficacy[i, j - 1, k] == 1:
                        
                        con_efficacy[i, j, k] = 1
                        con_futile[i, j, k] = 0
                    
                    else:
                        
                        con_efficacy[i, j, k] = efficacy[i, j, k]
                        con_futile[i, j, k] = futile[i, j, k]              
                          

    sys.stdout.write("Output Interim Analysis Data...")
    if not os.path.isdir(pathdir + "Probability"):
        
        os.makedirs(pathdir + "Probability")
        
    if not os.path.isdir(pathdir + "Interim Analysis"):
        
        os.makedirs(pathdir + "Interim Analysis")
    
    interim_dataset_copy = np.transpose(np.asarray(interim_crit), (2, 1, 0)).reshape((nsim * nStage), (nArm - 1))
    eff_dataset_copy = np.transpose(np.asarray(efficacy), (2, 1, 0)).reshape((nsim * nStage), (nArm - 1))
    fut_dataset_copy = np.transpose(np.asarray(futile), (2, 1, 0)).reshape((nsim * nStage), (nArm - 1))
    # stop_dataset_copy = np.transpose(np.asarray(stop), (2, 1, 0)).reshape((nsim * nStage), (nArm - 1))
    sim_df_index = [range(1, nsim + 1), range(1, nStage + 1)]
    
    interim_df = pd.DataFrame(interim_dataset_copy, index=pd.MultiIndex.from_product(sim_df_index, names=["# of Simulation", "Stage"]), columns=effColHeader[0:(nArm - 1)]).sort_index()
    eff_df = pd.DataFrame(eff_dataset_copy, index=pd.MultiIndex.from_product(sim_df_index, names=["# of Simulation", "Stage"]), columns=effColHeader[0:(nArm - 1)]).sort_index()
    fut_df = pd.DataFrame(fut_dataset_copy, index=pd.MultiIndex.from_product(sim_df_index, names=["# of Simulation", "Stage"]), columns=effColHeader[0:(nArm - 1)]).sort_index()
    # stop_df = pd.DataFrame(stop_dataset_copy, index=pd.MultiIndex.from_product(sim_df_index, names=["# Simulation", "Stage"]), columns=effColHeader[0:(nArm - 1)]).sort_index()
    
    con_eff_dataset_copy = np.transpose(np.asarray(con_efficacy), (2, 1, 0)).reshape((nsim * nStage), (nArm - 1))
    con_fut_dataset_copy = np.transpose(np.asarray(con_futile), (2, 1, 0)).reshape((nsim * nStage), (nArm - 1))
    con_eff_df = pd.DataFrame(con_eff_dataset_copy, index=pd.MultiIndex.from_product(sim_df_index, names=["# of Simulation", "Stage"]), columns=effColHeader[0:(nArm - 1)]).sort_index()
    con_fut_df = pd.DataFrame(con_fut_dataset_copy, index=pd.MultiIndex.from_product(sim_df_index, names=["# of Simulation", "Stage"]), columns=effColHeader[0:(nArm - 1)]).sort_index()
    # Output file
    interim_df.to_csv(pathdir + "Probability/Posterior Probability.csv")
    eff_df.to_csv(pathdir + "Interim Analysis/Unconditional Efficacy Data.csv")
    fut_df.to_csv(pathdir + "Interim Analysis/Unconditional Futile Data.csv")
    # stop_df.to_csv(pathdir + "Interim Analysisset/stop data.csv")
    con_eff_df.to_csv(pathdir + "Interim Analysis/Conditional Efficacy Data.csv")
    con_fut_df.to_csv(pathdir + "Interim Analysis/Conditional Futile Data.csv")

    # Calculate conditional futile, efficacy, and stop for each time
    interim_mean = np.sum(interim_crit, axis=2, dtype=np.float64) / nsim * 100
    con_futile_mean = np.sum(con_futile, axis=2, dtype=np.float64) / nsim * 100
    con_efficacy_mean = np.sum(con_efficacy, axis=2, dtype=np.float64) / nsim * 100    
    # Calculate unconditional futile, efficacy, and stop for each time
    futile_mean = np.sum(futile, axis=2, dtype=np.float64) / nsim * 100
    efficacy_mean = np.sum(efficacy, axis=2, dtype=np.float64) / nsim * 100
    
    
    # Conditional probabilities
    con_fut_list = con_futile_mean.tolist()
    con_eff_list = con_efficacy_mean.tolist()
    fut_list = futile_mean.tolist()
    eff_list = efficacy_mean.tolist()
    
    # Output file to pdf
    # Plot color
    color_map = [(31, 119, 180), (174, 199, 232), (255, 127, 14), (255, 187, 120),
             (44, 160, 44), (152, 223, 138), (214, 39, 40), (255, 152, 150),
             (148, 103, 189), (197, 176, 213), (140, 86, 75), (196, 156, 148),
             (227, 119, 194), (247, 182, 210), (127, 127, 127), (199, 199, 199),
             (188, 189, 34), (219, 219, 141), (23, 190, 207), (158, 218, 229)] 
        
    color_list = random.sample(color_map, nArm)
    for color_i in range(0, len(color_list)):
            
        r, g, b = color_list[color_i]
        color_list[color_i] = (r / 255., g / 255., b / 255.)   
    

    sys.stdout.write("Output histogram plot for posterior probability...")
    # Plot for critical value histogram
    for m in range(0, nArm - 1):
            
        for p in range(0, nStage):
                    
            sys.stdout.write("Output histograms for probability of treatment %d at stage %d"%(m + 1, p + 1))                                    
            fig = plt.figure(figsize=(5.0, 5.0))
            ax = fig.add_subplot(111)
            ax.hist(interim_crit[m, p, :], normed=False, color=color_list[m], bins=10)
            ax.tick_params(axis='both', which='major', labelsize=15)
            ax.tick_params(axis='both', which='minor', labelsize=15)             
            plt.title("Treatment Arm %d at Stage %d" % ((m + 1), (p + 1)), fontsize=15)         
            plt.xticks(np.arange(0, 1, 0.2))
            plt.xlim(0, 1)
            if predNum[m, p] == 0:
                
                plt.xlabel("Posterior Probability", fontsize=15)
            
            else: 
                
                plt.xlabel("Predictive Probability", fontsize=15)
                                
            plt.ylabel("Frequency", fontsize=15)
            filename = "Treatment Arm " + str(m + 1) + " at Stage " + str(p + 1)
            plt.tight_layout()
            plt.savefig(pathdir + "Probability/" + filename + ".png")
            plt.clf()
            plt.close()
            
    fig = plt.figure(figsize=(3.0, 3.0))
    ax = fig.add_subplot(111)
    ax.hist(interim_crit[0, 0, :], normed=False, color=random.choice(color_list))   
    plt.xticks(rotation="vertical")
    plt.tight_layout()
    plt.savefig(pathdir + "Probability/ui.png")
    plt.clf()
    plt.close()

    
    # Plot for unconditional/conditional probability of stopping for efficacy/futility
    fig = plt.figure(figsize=(5.0, 5.0))
    ax = fig.add_subplot(111)
    for m in range(0, nArm - 1):
        
        sys.stdout.write("Output plot of conditional futility of treatment %d"%(m + 1))                                    
        x3 = range(1, nStage + 1)
        y3 = np.asarray(con_futile_mean[m, :]) / 100
        plt.plot(x3, y3, marker="o", markersize=8, linestyle="-", color=color_list[m], label=effColHeader[m])

    min_y3 = np.min(con_futile_mean / 100)
    max_y3 = np.max(con_futile_mean / 100)
    ax.set_ylim([max(-0.05, min_y3 - 0.05), min(max_y3 + 0.05, 1.05)])
    plt.xticks(range(1, nStage + 1), patColHeader)
    # plt.tick_params(axis='both', which='major', labelsize=15)
    # plt.tick_params(axis='both', which='minor', labelsize=15)             
    plt.title("Probability of Stopping for Futility", fontsize=15)         
    plt.ylabel("Probability of Stopping(%)", fontsize=15)
    fig.set_tight_layout(True)
    lgd = plt.legend(loc=2, bbox_to_anchor=(1.0, 0.5))
    plt.savefig(pathdir + "Interim Analysis/Conditional Probability Futility.png", bbox_extra_artists=(lgd,), bbox_inches="tight")      
    plt.close()
    
    fig = plt.figure(figsize=(5.0, 5.0))
    ax = fig.add_subplot(111)
    for m in range(0, nArm - 1):

        sys.stdout.write("Output plot of conditional efficacy of treatment %d"%(m + 1))           
        x3 = range(1, nStage + 1)
        y3 = np.asarray(con_efficacy_mean[m, :]) / 100
        plt.plot(x3, y3, marker="o", markersize=8, linestyle="-", color=color_list[m], label=effColHeader[m])
    
    min_y3 = np.min(con_efficacy_mean / 100)
    max_y3 = np.max(con_efficacy_mean / 100)
    ax.set_ylim([max(-0.05, min_y3 - 0.05), min(max_y3 + 0.05, 1.05)])
    plt.xticks(range(1, nStage + 1), patColHeader)
    # plt.tick_params(axis='both', which='major', labelsize=15)
    # plt.tick_params(axis='both', which='minor', labelsize=15)             
    plt.title("Probability of Stopping for Efficacy", fontsize=15)         
    plt.ylabel("Probability of Stopping(%)", fontsize=15)
    lgd = plt.legend(loc=2, bbox_to_anchor=(1.0, 0.5))
    plt.savefig(pathdir + "Interim Analysis/Conditional Probability Efficacy.png", bbox_extra_artists=(lgd,), bbox_inches="tight")      
    plt.close()
    
    # Unconditional probabilities
    sys.stdout.write("Output Unconditional Probabilities...")
    fig = plt.figure(figsize=(5.0, 5.0))
    ax = fig.add_subplot(111)
    for m in range(0, nArm - 1):

        sys.stdout.write("Output plot of unconditional futility of treatment %d"%(m + 1))   
        x3 = range(1, nStage + 1)
        y3 = np.asarray(futile_mean[m, :]) / 100
        plt.plot(x3, y3, marker="o", markersize=8, linestyle="-", color=color_list[m], label=effColHeader[m])
    
    min_y3 = np.min(futile_mean / 100)
    max_y3 = np.max(futile_mean / 100)
    ax.set_ylim([max(-0.05, min_y3 - 0.05), min(max_y3 + 0.05, 1.05)])
    plt.xticks(range(1, nStage + 1), patColHeader)    
    # plt.tick_params(axis='both', which='major', labelsize=15)
    # plt.tick_params(axis='both', which='minor', labelsize=15)             
    plt.title("Probability of Stopping for Futility", fontsize=15)         
    plt.ylabel("Probability of Stopping(%)", fontsize=15)
    lgd = plt.legend(loc=2, bbox_to_anchor=(1.0, 0.5))
    plt.savefig(pathdir + "Interim Analysis/Unconditional Probability Futility.png", bbox_extra_artists=(lgd,), bbox_inches="tight")      
    plt.close()
    
    # Unconditional efficacy
    fig = plt.figure(figsize=(5.0, 5.0))
    ax = fig.add_subplot(111)
    for m in range(0, nArm - 1):

        sys.stdout.write("Output plot of unconditional efficacy of treatment %d"%(m + 1))   
        x3 = range(1, nStage + 1)
        y3 = np.asarray(efficacy_mean[m, :]) / 100
        plt.plot(x3, y3, marker="o", markersize=8, linestyle="-", color=color_list[m], label=effColHeader[m])
    
    min_y3 = np.min(efficacy_mean / 100)
    max_y3 = np.max(efficacy_mean / 100)
    ax.set_ylim([max(-0.05, min_y3 - 0.05), min(max_y3 + 0.05, 1.05)]) 
    plt.xticks(range(1, nStage + 1), patColHeader)
    # plt.tick_params(axis='both', which='major', labelsize=15)
    # plt.tick_params(axis='both', which='minor', labelsize=15)             
    plt.title("Probability of Stopping for Efficacy", fontsize=15)         
    plt.ylabel("Probability of Stopping(%)", fontsize=15)
    lgd = plt.legend(loc=2, bbox_to_anchor=(1.0, 0.5))
    plt.savefig(pathdir + "Interim Analysis/Unconditional Probability Efficacy.png", bbox_extra_artists=(lgd,), bbox_inches="tight")      
    plt.close()
    
    fig = plt.figure(figsize=(3.0, 3.0))
    ax = fig.add_subplot(111)
    min_y3 = np.min(y3)
    max_y3 = np.max(y3)
    ax.set_ylim([max(-0.05, min_y3 - 0.05), min(max_y3 + 0.05, 1.05)])
    ax.plot(x3, y3, marker="o", markersize=8, linestyle="-", color=random.choice(color_list))     
    fig.set_tight_layout(True)
    plt.savefig(pathdir + "Interim Analysis/ui.png")
    plt.close()
    
    # Del x1, x2, x3, y1, y2, y3
    # Free pointer
    del con_fut_list, con_eff_list, fut_list, eff_list
    del x3, y3, interim_dict
    free(interim_crit_pointer)
    free(futile_pointer)
    free(efficacy_pointer)
    free(stop_pointer)
    free(con_futile_pointer)
    free(con_efficacy_pointer)    
    return interim_mean, con_futile_mean, con_efficacy_mean, futile_mean, efficacy_mean



# Python functions
# Interim analysis based on posterior predictive probability
def InterimPredCheck(nsim, nArm, nStage, prior, eff, fut, clinSig, sim_dataset, tps_array,
                     predNum, predSuccess, gamma_nsim, gamma_vect, pathdir,
                     effColHeader, patColHeader):   
    
    try: 
        
        interim_mean, con_futile_mean, con_efficacy_mean, futile_mean, efficacy_mean = FixedInterimPredCheck(nsim, nArm, nStage, prior, eff, fut, clinSig, sim_dataset, tps_array,
                                predNum, predSuccess, gamma_nsim, gamma_vect, pathdir,
                                effColHeader, patColHeader)
        return interim_mean, con_futile_mean, con_efficacy_mean, futile_mean, efficacy_mean

    except:
        
        sys.stdout.write("Oops, fail to simulate interim analysis!")