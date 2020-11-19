import os
import math
import numpy as np
import matplotlib.pyplot as plt

def trough_standardization(column, dev_min, dev_max):
    
    #************************************************************************************************************
    #
    # Standardizes the voltage data for each channel by identifying large deviances in voltages as troughs.
    #
    # INPUT:    List of voltage values as floats.
    #
    # PROCESS:  Voltage values are rounded to two decimal places and appended to the volt_column. A confidence
    #           interval is defined aroudn the mean voltage value using a low (min_value) and high (max_value)
    #           threshold. These values can be defined by the user according to the characteristics of the
    #           voltage recording data. Voltages at or higher than the min value of the confidence interval
    #           are set to 0 while voltages far below the min_value are set to 1 and identity the presence
    #           of a trough. Thus, a trough can be defined as any large deviance in voltage that is due to
    #           noise or chance. Finally, a list of troughs is created after compressing sequences of 
    #           trough-like identifiers into a single identifier (e.g. compressed sequences of 1s to a single
    #           1 to denote a trough).
    #
    #           Threshold values can be modified accordingly. They are labeled with a '*'. The default values
    #           are set to deliver a fine tune signal standardization.
    #
    # OUTPUT:   List of 1s and 0s where 1 designates the presence of a trough and 0 designates no trough.
    #
    #************************************************************************************************************

    volt_column = [] 
    int_list =[] # sequences of 0s and 1s. 
    troughs=[]
    
    for i in range(0, len(column)): 
        volt_column.append(round(column[i], 2))
    
    channel_mean = (sum(volt_column)/len(volt_column))
    min_val=round(channel_mean - dev_min, 2) # * 
    max_val=round(channel_mean + dev_max, 2) # *
 
    for v in range(0, len(volt_column)):  
        x=(volt_column[v]-min_val)/(max_val-min_val) 
        if x < -2:  # *
            int_list.append(1)  
        else:
            int_list.append(0)

    for j in range(0, len(int_list)-1): 
        if int_list[j] > int_list[j-1] and int_list[j] >= int_list[j+1]: 
            troughs.append(1)
        else:
            troughs.append(0)

    troughs.append(0)

    print("   Num of 1's:", sum(int_list), "   Num of troughs:", sum(troughs),
          "   Min Dev: ", dev_min, "   Max Dev: ", dev_max)
    
    return troughs 

def plot_diagnostics(deviations, file_number, figure, axs):
    
    #************************************************************************************************************
    #
    # Plot diagnostics to identity noise or files with overly-sensitive troughs.
    #
    # INPUT:    deviations as a list of floats, file_number as an int, the figure, and axs as a subplot. 
    #
    # PROCESS:  Files with little noise and large troughs will be durable to small changes in deviations. Default
    #           here is to test and plot how changes in the min and max deviation values change the number of
    #           troughs; however, other threshold values such as max deviation and the x value threshold.
    #
    # OUTPUT:   Returns the standardized voltage column as a list of 1s and 0s where 1 designates the presence
    #           of a trough and 0 designates no trough. Plots diagnositcs of all the recoridng files in a
    #           directory.
    #
    #************************************************************************************************************
    
    f = file_number*10
    
    for volt_dev_min in deviations:
        num_troughs = []
        for volt_dev_max in deviations:
            troughs_col = trough_standardization(voltage_column, volt_dev_min, volt_dev_max)
            num_troughs.append(sum(troughs_col))
            
        axs = axs.flatten()
        axs[f].plot(deviations, num_troughs, linestyle='--', marker='o', color='b')
        axs[f].set_ylim([min(num_troughs)-1, max(num_troughs)+1])
        axs[f].title.set_text(file + '\nMax-Min=%i' %(max(num_troughs)-min(num_troughs)))
        axs[f].set_xlabel("Max Val")
        axs[f].set_ylabel("Number of Troughs")
        axs[f].text(0.75, 0.9, "Min Val=%.2f" %volt_dev_min, ha='center', va='center', transform=axs[f].transAxes)
        
        for x,y in zip(deviations, num_troughs):
            label=y
            axs[f].annotate(label,(x,y), textcoords="offset points", xytext=(10,5), ha='center')

        f += 1

    return troughs_col

def map_diagnostics(deviations, f, heat_map, axs):

    #************************************************************************************************************
    #
    # Generate heat maps to diagnose files with noise or overly-sensitive troughs.
    #
    # INPUT:    deviations as a list of floats, file number (f) as an int, the figure, and axs as a subplot. 
    #
    # PROCESS:  Files with little noise and large troughs will be durable to small changes in deviations. Default
    #           here is to test and plot how changes in the min and max deviation values change the number of
    #           troughs; however, other threshold values such as max deviation and the x value threshold.
    #
    # OUTPUT:   Returns the standardized voltage column as a list of 1s and 0s where 1 designates the presence
    #           of a trough and 0 designates no trough. Generates heat map diagnostics of all the recoridng files
    #           in a directory.
    #
    #************************************************************************************************************
    
    all_troughs = []
    for volt_dev_min in deviations:
        num_troughs = []
        for volt_dev_max in deviations:
            troughs_col = trough_standardization(voltage_column, volt_dev_min, volt_dev_max)
            num_troughs.append(sum(troughs_col))
        all_troughs.append(num_troughs)

    a = np.array(all_troughs)
    axs = axs.flatten()
    im = axs[f].imshow(a, cmap='viridis', interpolation='nearest') # cmap='hot'

    axs[f].title.set_text(file + '\nMax-Min=%i' %(np.max(all_troughs)-np.min(all_troughs)))
    axs[f].set_xticks(np.arange(len(deviations)))
    axs[f].set_yticks(np.arange(len(deviations)))
    axs[f].set_xticklabels(deviations, fontsize=8)
    axs[f].set_yticklabels(deviations, fontsize=8)
    axs[f].set_xlabel("Max Dev Val", fontsize=12)
    axs[f].set_ylabel("Min Dev Val", fontsize=12)

    cbar = heat_map.colorbar(im, ax=axs[f], fraction=0.046, pad=0.03)
    cbar.ax.set_ylabel("Number of Troughs", rotation=-90, va="bottom")
    
    rows, cols = a.shape
    for i in range(rows):
        for j in range(cols):
            text = axs[f].text(j, i, a[i, j], ha="center", va="center", color="w", fontsize=6)
    
    return troughs_col

#************************************************************************************************************
#   To call the recording data file, write the complete file directory path below. An example path is
#   r"/Users/username/Desktop/Flight_scripts/". The number of columns processed below depends on the number
#   of channels used to record the flight data. For individual insects with only two columns per file,
#   only the TBF and voltage reading columns are processed. However, if the number of channels is different
#   the script needs to be edited accordingly.
#************************************************************************************************************

if __name__=="__main__":
    
    #main_path = r"/Users/anastasiabernat/Desktop/git_repositories/undergrad-collabs/max_speed/" # input the path to the Flight_scripts directory here 
    main_path = r"/Users/anastasiabernat/Desktop/Dispersal/Trials-Winter2020/" 
    path = main_path + "set_files/"
    dir_list = sorted(os.listdir(path))

    # scatter plot
    #rows = math.ceil(len(dir_list) / 5) * 2
    #fig, axes = plt.subplots(rows,5, figsize=(20, 4*rows), facecolor='w', edgecolor='k')
    #fig.tight_layout(pad=6.0)

    # heat map
    hrows = math.ceil(len(dir_list) / 5)  
    hmap, haxes = plt.subplots(hrows,5, figsize=(20, 4*hrows), facecolor='w', edgecolor='k')
    hmap.tight_layout(pad=5.4)

    print("Files in '", path, "' :")

    file_num = 0
    for file in dir_list:
        
        print("\n", file)
        filepath = path + str(file)
        InputFile = open(filepath, mode="r", encoding='latin-1')
        Lines = InputFile.readlines()
        
        time_column = []
        voltage_column = []

        for i in range(0, len(Lines)):
            raw = Lines[i]
            a,b,c = raw.split(",") 
            time_column.append(float(a)) 
            voltage_column.append(float(b)) 

        InputFile.close()

        devs = [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10]
        #trough_col = plot_diagnostics(devs, file_num, fig, axes) # * Comment out this line after running diagnostics
        trough_col = map_diagnostics(devs, file_num, hmap, haxes) # * Comment out this line after running diagnostics
        file_num += 1

        #************************************************************************************************************
        #   After running diagnostics, define the trough_col with specific min and max deviation values in the
        #   trough_standardization function below if desired. The default here is a min deviation and max deviation
        #   value of 0.1 V.
        #************************************************************************************************************
        
        #trough_col = trough_standardization(voltage_column, 0.1, 0.1) # * Uncomment this line after running diagnostics

        out_path = r"/Users/anastasiabernat/Desktop/git_repositories/undergrad-collabs/max_speed/"
        outpath = out_path + "standardized_files/"
        OutputFile = open(outpath + "standardized_" + str(file), mode="w")
        for i in range(0, len(Lines)):
            OutputFile.write('%.2f' % time_column[i] + ", " +
                             '%.2f' % trough_col[i] + "\n")
        OutputFile.close()

    #fig.savefig("trough_diagnostic.png") 
    hmap.savefig("trough_diagnostic.png")

#**********************************************************************************************
# This file has been modified from Attisano et al. 2015.
#**********************************************************************************************
