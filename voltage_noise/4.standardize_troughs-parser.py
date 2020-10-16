import os
import math
import argparse

import numpy as np
import matplotlib.pyplot as plt

def trough_standardization(column, dev_min, dev_max):
    
    #************************************************************************************************************
    #
    # Standardizes the voltage data for each channel by identifying large deviances in voltages as troughs.
    #
    # INPUT:    List of voltage values as floats, the minimum deviation value as a float, and the maximum
    #           deviation value as a float.
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
    min_val=round(channel_mean - dev_min, 2)
    max_val=round(channel_mean + dev_max, 2)
 
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

def map_diagnostics(deviations, f, heat_map, axs):

    #************************************************************************************************************
    #
    # Generate heat maps to diagnose files with noise or overly-sensitive troughs.
    #
    # INPUT:    deviations as a list of floats, file number (f) as an int, the figure (heat_map), and axs as
    #           a subplot. 
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
    im = axs[f].imshow(a, cmap='viridis', interpolation='nearest')

    axs[f].title.set_text(file + '\nMax-Min=%i' %(max(all_troughs)[0]-min(all_troughs)[-1]))
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
            text = axs[f].text(j, i, a[i, j], ha="center", va="center", color="w", fontsize=5.5)
    
    return troughs_col

def str2bool(s):
    
    #************************************************************************************************************
    #
    # Convert a string to a boolean (True or False).
    #
    # INPUT:    A string, s, that can be a set of positive, affirmative, or boolean-like strings that denote True
    #           or a set of negative or boolean-like strings that denote False.
    #
    # OUTPUT:   A boolean True for all positive, affirmative, or boolean-like strings or a boolean False for all
    #           negative or boolean-like strings.
    #
    #************************************************************************************************************

    if isinstance(s, bool):
       return s
    if s.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif s.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

#************************************************************************************************************
#
#   Easy to write user-friendly command-line interfaces are coded below using the argparse module. To
#   access all arguments, the user can type the following in their terminal command line:
#
#   $ python3 standardize_troughs-parser.py -h 
#
#   Which will output the following:
#
#   usage: standardize_troughs-parser.py [-h] -p  -d  -s  -m  -M
#
#   Standardize and diagnose recording txt files.
#   
#   optional arguments:
#     -h, --help           show this help message and exit
#     -p , --path          Set path to the Python scripts directory.
#     -d , --diagnose      Run heat map diagnostics (True). Do not run (False).
#     -s , --standardize   Run final standardizations (True). Do not run (False).
#     -m , --min           Select minimum deviation value.
#     -M , --max           Select maximum deviation value.
#
#   To input arguments the user can type the path, boolean values, & min and max values after each argument,
#   such as:
#
#   $ python3 standardize_troughs.py -p /Users/username/Desktop/Flight_scripts/ -d True -s False -m 0.1 -M 0.1
#
#************************************************************************************************************

parser = argparse.ArgumentParser(description='Standardize and diagnose recording txt files.')
parser.add_argument('-p', '--path', type=str, metavar='', required=True, 
                    help='Set path to the Python scripts directory.')
parser.add_argument('-d', '--diagnose', type=str2bool, metavar='', required=True,
                    help='Run heat map diagnostics (True). Do not run (False).')
parser.add_argument('-s', '--standardize', type=str2bool, metavar='', required=True,
                    help='Run final standardizations (True). Do not run (False).')
parser.add_argument('-m', '--min', type=float, metavar='', required=True,
                    help='Select minimum deviation value.')
parser.add_argument('-M', '--max', type=float, metavar='', required=True,
                    help='Select maximum deviation value.')
args = parser.parse_args()

main_path = args.path
path = main_path + "test_files/"
dir_list = sorted(os.listdir(path))

run_diagnostics = args.diagnose
run_standardizations = args.standardize

hrows = int(math.ceil(len(dir_list) / 5))
hmap, haxes = plt.subplots(hrows,5, figsize=(20, 4*hrows), facecolor='w', edgecolor='k')
hmap.tight_layout(pad=5.1) 

#************************************************************************************************************
#   The number of columns processed below depends on the number of channels used to record the flight data.
#   For individual insects with only two columns per file, only the TBF and voltage reading columns are
#   processed. However, if the number of channels is different the script needs to be edited accordingly.
#************************************************************************************************************

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
    
    if run_diagnostics:
        trough_col = map_diagnostics(devs, file_num, hmap, haxes) 
    file_num += 1

    #************************************************************************************************************
    #   After running diagnostics, define the trough_col with specific min and max deviation values in the
    #   trough_standardization function below. The default here is a min deviation and max deviation value
    #   of 0.1 V.
    #************************************************************************************************************

    if run_standardizations:
        trough_col = trough_standardization(voltage_column, args.min, args.max) 
    
    outpath = main_path + "standardized_files/"
    OutputFile = open(outpath + "standardized_" + str(file), mode="w")
    for i in range(0, len(Lines)):
        OutputFile.write('%.2f' % time_column[i] + ", " +
                         '%.2f' % trough_col[i] + "\n")
    OutputFile.close()

if run_diagnostics:
    hmap.savefig("heatmap_trough_diagnostic.png")

#**********************************************************************************************
# This file has been adopted from Attisano et al. 2015.
#**********************************************************************************************
