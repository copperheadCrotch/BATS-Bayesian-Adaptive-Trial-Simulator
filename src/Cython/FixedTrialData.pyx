import cython
cimport cython

from cython_gsl cimport *
from libc.stdlib cimport malloc, free


# Import python modules
import numpy as np
cimport numpy as np
import sys
import random
import pandas as pd
# Plot module
import matplotlib.pyplot as plt



# Cython function to simulate the outcome
@cython.boundscheck(False)
@cython.wraparound(False)
@cython.cdivision(True)
cdef TrialData(int nsim, int seed, int nArm, int nStage, double [::1] te_list, int [:, ::1] ps_array, int [:, :, ::1] sim_dataset, str pathdir, list effColHeader):
    
    cdef Py_ssize_t i, j, k, color_i
    cdef int r, g, b
    cdef float mean_success, prob_success
    cdef int *stage_dataset_pointer = <int *>malloc(nArm * nStage * nsim * sizeof(int))
    cdef int [:, :, ::1] stage_dataset = <int[:nArm, :nStage, :nsim]> stage_dataset_pointer
    cdef gsl_rng *binomial_r = gsl_rng_alloc(gsl_rng_mt19937)
    # Set seed
    gsl_rng_set(binomial_r, seed)
    
    # Generate the trial outcomes
    sys.stdout.write("Generate the trial dataset...")
    # Simulate the data
    for i in range(0, nArm):
        
        for j in range(0, nStage):
        
            for k in xrange(0, nsim):
            
                stage_dataset[i, j, k] = gsl_ran_binomial(binomial_r, te_list[i], ps_array[i, j])
                if j > 0:
                    
                    sim_dataset[i, j, k] = sim_dataset[i, j - 1, k] + stage_dataset[i, j, k]
                
                else:
                    
                    sim_dataset[i, j, k] = stage_dataset[i, j, k]
                
    # Free the pointer
    gsl_rng_free(binomial_r)
    
    # Output simulated data  
    try:
        
        if str(pathdir) == "":
            
            # Use cumulative dataset for further study
            free(stage_dataset_pointer)
            return
        
        import os
        if not os.path.isdir(pathdir + "Number of Success"):
        
            os.makedirs(pathdir + "Number of Success")
        
        if not os.path.isdir(pathdir + "Number of Cumulative Success"):
        
            os.makedirs(pathdir + "Number of Cumulative Success")
            
        sys.stdout.write("Output simulated data...")
        # Success in each stage each arm
        stage_dataset_copy = np.transpose(np.asarray(stage_dataset), (2, 1, 0)).reshape((nsim * nStage), nArm)
        sim_df_index = [range(1, nsim + 1), range(1, nStage + 1)]
        sim_df = pd.DataFrame(stage_dataset_copy, index=pd.MultiIndex.from_product(sim_df_index, names=["# of Simulation", "Stage"]), columns=effColHeader).sort_index()
        sim_df.to_csv(pathdir + "Number of Success/Simulated Data.csv")
        # Cumulative success by stage each arm
        cum_sim_df = pd.DataFrame(np.transpose(np.array(sim_dataset), (2, 1, 0)).reshape((nsim * nStage), nArm), index=pd.MultiIndex.from_product(sim_df_index, names=["# Simulation", "Stage"]), columns=effColHeader).sort_index()
        cum_sim_df.to_csv(pathdir + "Number of Success/Cumulative Simulated data.csv")
        
        # Plot
        color_map = [(31, 119, 180), (174, 199, 232), (255, 127, 14), (255, 187, 120),    
             (44, 160, 44), (152, 223, 138), (214, 39, 40), (255, 152, 150),    
             (148, 103, 189), (197, 176, 213), (140, 86, 75), (196, 156, 148),    
             (227, 119, 194), (247, 182, 210), (127, 127, 127), (199, 199, 199),    
             (188, 189, 34), (219, 219, 141), (23, 190, 207), (158, 218, 229)] 
        
        color_list = random.sample(color_map, nArm)
        for color_i in range(0, len(color_list)):
            
            r, g, b = color_list[color_i]
            color_list[color_i] = (r/255., g/255., b/255.)
            
        sys.stdout.write("Output histogram plots for simulated data...")
        
        for i in range(0, nArm):
            
            for j in range(0, nStage):
                
                fig = plt.figure(figsize = (5.0, 5.0))
                ax = fig.add_subplot(111)
                ax.hist(stage_dataset[i, j, :], normed = False, color = color_list[i], label = effColHeader[i])
                mean_success = np.mean(stage_dataset[i, j, :])
                prob_success = mean_success/ps_array[i, j]
                ax.tick_params(axis='both', which='major', labelsize=15)
                ax.tick_params(axis='both', which='minor', labelsize=15)
                filename = ""
                if i != nArm - 1:
               
                    plt.title("Treatment Arm %d at Stage %d"%(i + 1, j + 1), fontsize = 15)
                    filename = "Treatment Arm " + str(i + 1) + " at Stage " + str(j + 1)

                
                elif i == nArm -1:
                    
                    plt.title("Control Arm at Stage %d"%(j + 1), fontsize = 15)
                    filename = "Control Arm at Stage " + str(j + 1)

                
                plt.xlabel("Number of Success", fontsize = 15)
                plt.ylabel("Frequency", fontsize = 15)
                fig.set_tight_layout(True)
                plt.savefig(pathdir + "Number of Success/" + filename + ".png")
                
                plt.close()

        fig = plt.figure(figsize = (3.0, 3.0))
        ax = fig.add_subplot(111)
        ax.hist(stage_dataset[0, 0, :], normed = False, color = random.choice(color_list))     
        fig.set_tight_layout(True)
        plt.savefig(pathdir + "Number of Success/ui.png")
        
        plt.close()
        """
        # Plot
        plt.figure(figsize = (5.0 * nStage, 5.0 * nArm))
        for i in range(0, nArm):
            
            for j in range(0, nStage):
                
                ax = plt.subplot(nArm, nStage, i * nStage + j +  1)
                ax.hist(stage_dataset[i, j, :], normed = True, color = color_list[i])
                mean_success = np.mean(stage_dataset[i, j, :])
                prob_success = mean_success/ps_array[i, j]
                textstr = "Mean=%.2f\nP(Success)=%.2f"%(mean_success, prob_success)
                ax.text(0.05, 0.95, textstr, verticalalignment = "top", horizontalalignment = "left", transform=ax.transAxes,  fontsize = 12)
                ax.tick_params(axis='both', which='major', labelsize=15)
                ax.tick_params(axis='both', which='minor', labelsize=15)
                
                if i != nArm - 1:
               
                    plt.title("Treatment Arm %d at Stage %d"%(i + 1, j + 1), fontsize = 15)
                
                else:
                    
                    plt.title("Control Arm at Stage %d"%(j + 1), fontsize = 15)
                
                plt.xlabel("Number of Success", fontsize = 15)
                plt.ylabel("Frequency", fontsize = 15)
                
                
        plt.suptitle("Distribution of Simulated Data", fontsize = 20)
        # plt.tight_layout(pad=1.0, w_pad=1.0, h_pad=1.0)
        plt.tight_layout()
        plt.subplots_adjust(top = 0.9, hspace = 0.3, wspace = 0.3)
        plt.savefig(pathdir + "Simulated Dataset/Histogram of Simulated Data.png")
        plt.close()
        sys.stdout.write("Output histogram plots for cumulative simulated data...")
        """
        # Cumulative plot
        tps_array = np.cumsum(np.array(ps_array), axis = 1)
        for i in range(0, nArm):
            
            for j in range(0, nStage):
                
                fig = plt.figure(figsize = (5.0, 5.0))
                ax = fig.add_subplot(111)
                ax.hist(sim_dataset[i, j, :], normed = False, color = color_list[i], label = effColHeader[i])
                cum_mean_success = np.mean(sim_dataset[i, j, :])
                cum_prob_success = cum_mean_success/tps_array[i, j]
                ax.tick_params(axis='both', which='major', labelsize=15)
                ax.tick_params(axis='both', which='minor', labelsize=15)
                if i != nArm - 1:
               
                    plt.title("Treatment Arm %d at Stage %d"%(i + 1, j + 1), fontsize = 15)
                    filename = "Treatment Arm " + str(i + 1) + " at Stage " + str(j + 1)

                
                elif i == nArm -1:
                    
                    plt.title("Control Arm at Stage %d"%(j + 1), fontsize = 15)
                    filename = "Control Arm at Stage " + str(j + 1)

                
                plt.xlabel("Number of Success", fontsize = 15)
                plt.ylabel("Frequency", fontsize = 15)
                fig.set_tight_layout(True)
                plt.savefig(pathdir + "Number of Cumulative Success/" + filename + ".png")
                
                plt.close()

        fig = plt.figure(figsize = (3.0, 3.0))
        ax = fig.add_subplot(111)
        ax.hist(sim_dataset[nArm - 1, nStage - 1, :], normed = False, color = random.choice(color_list))     
        fig.set_tight_layout(True)
        plt.savefig(pathdir + "Number of Cumulative Success/ui.png")
        
        plt.close()
        
        # Use cumulative dataset for further study
        del stage_dataset_copy, sim_df, cum_sim_df, tps_array
        free(stage_dataset_pointer)
        return
        
    except:
        
        sys.stdout.write("Oops! Fail to output the simulated data")
        sim_dataset = np.cumsum(np.array(sim_dataset), axis = 1)
        return
    
    
# Fixed trial data generating function
def FixedTrialData(nsim, seed, nArm, nStage, te_list, ps_array, sim_dataset, pathdir, effColHeader):
    
    TrialData(nsim, seed, nArm, nStage, te_list, ps_array, sim_dataset, pathdir, effColHeader)
    