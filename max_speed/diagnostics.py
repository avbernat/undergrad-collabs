import os
import math
import numpy as np
import matplotlib.pyplot as plt

from standardize_troughs import trough_standardization
from flight_analysis import time_list, speed_list, distance

def standardize(filepath, min_dev, max_dev, trough_standardization):

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
    
    trough_column = trough_standardization(voltage_column, min_dev, max_dev) 

    return (time_column, trough_column)

def analyze(time_column, trough_column, time_list, speed_list, distance):

    time_channel = time_list(time_column, trough_column)
    speed_channel = speed_list(time_channel)
    time_n, speed_n, dist, av_speed = distance(time_channel, speed_channel)
    
    return (round(av_speed,2), round(dist,2))

##def get_summary(file_name, dtroughs):
##
##    chamber_ID = None
##    threshold = 15
##
##    if dtroughs > 0 and dtroughs < threshold: # small change
##        dsmall_count = 1 
##
##    if dtroughs >= threshold: # large change
##        chamber_ID = file_name.split("-")[-1].split(".")[0]
##        dlarge_count = 1
##
##    return dsmall_count, dlarge_count, chamber_ID

def heat_map(deviations, f, heat_map, axs, matrix, filename, bar_title):

    a = np.array(matrix)
    axs = axs.flatten()
    im = axs[f].imshow(a, cmap='viridis', interpolation='nearest') # cmap='hot'

    delta_stat = np.max(matrix)-np.min(matrix)

    axs[f].title.set_text(filename + '\nMax-Min=%.2f' %delta_stat)
    axs[f].set_xticks(np.arange(len(deviations)))
    axs[f].set_yticks(np.arange(len(deviations)))
    axs[f].set_xticklabels(deviations, fontsize=8)
    axs[f].set_yticklabels(deviations, fontsize=8)
    axs[f].set_xlabel("Max Dev Val", fontsize=12)
    axs[f].set_ylabel("Min Dev Val", fontsize=12)

    cbar = heat_map.colorbar(im, ax=axs[f], fraction=0.046, pad=0.03)
    cbar.ax.set_ylabel(bar_title, rotation=-90, va="bottom")
    
    rows, cols = a.shape
    for i in range(rows):
        for j in range(cols):
            text = axs[f].text(j, i, a[i, j], ha="center", va="center", color="w", fontsize=6)
    
#main_path = r"/Users/anastasiabernat/Desktop/git_repositories/undergrad-collabs/max_speed/"
main_path = r"/Users/anastasiabernat/Desktop/Dispersal/Trials-Winter2020/"
path = main_path + "split_files/"
dir_list = sorted(os.listdir(path))

# Rearranging the directory_list into list of files by set. 

max_set_num = int(dir_list[-1].split("_")[1].split("-")[0].split("t0")[-1])

sets = []
for i in range(1, max_set_num + 1):
    if i < 10:
        s=f"00{i}"
    else:
        s=f"0{i}"
    set_name = f"set{s}"
    set_list = []
    for file in dir_list:
        if set_name in file:
            set_list.append(file)
    sets.append(set_list)

##total_small_changes = 0
##total_large_changes = 0
##large_changes_chamber_ID = []

set_number=16 # choose your set here
sets = [sets[set_number-1]] 

for set_list in sets:

    # trough heat map
    rows = math.ceil(len(set_list) / 5) 
    fig, axes = plt.subplots(rows,5, figsize=(20, 4*rows), facecolor='w', edgecolor='k')
    fig.tight_layout(pad=6.0)

    # speed and distance heat map
    r = rows * 2
    hmap, haxes = plt.subplots(r,5, figsize=(20, 4*r), facecolor='w', edgecolor='k')
    hmap.tight_layout(pad=6.0)

    f=0
    h=0
    
    for file in set_list:
        
        print("\n", file)
        file_path = path + str(file)
        set_n = file.split("_")[1].split("-")[0]
        
        devs = [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10]
        all_troughs = []
        all_speeds = []
        all_distances = []
        for min_dev_val in devs:
            print(f"     Calculating...{len(devs)} troughs, speeds, and distances at min dev value of {min_dev_val}.")
            troughs = []
            speeds = []
            distances = []
            for max_dev_val in devs:
                (time_col, trough_col) = standardize(file_path, min_dev_val, max_dev_val, trough_standardization)
                (avg_speed, total_dist) = analyze(time_col, trough_col, time_list, speed_list, distance)
                troughs.append(sum(trough_col))
                speeds.append(avg_speed)
                distances.append(total_dist)
            all_troughs.append(troughs)
            all_speeds.append(speeds)
            all_distances.append(distances)
        
        # delta_trough = heat_map(devs, f, fig, axes, all_troughs, file, "Number of Troughs")
        heat_map(devs, f, fig, axes, all_troughs, file, "Number of Troughs")
        #dsmall, dlarge, c_id = get_summary(file, delta_stat)
        f+=1
        heat_map(devs, h, hmap, haxes, all_speeds, file, "Average Speed (m/s)")
        h+=1
        heat_map(devs, h, hmap, haxes, all_distances, file, "Distance (m/s)")
        h+=1

##        total = f
##        total_small_changes += dsmall
##        total_large_changes += dlarge
##        large_changes_chamber_ID.append(c_id)

##    no_change_count = total - (total_large_changes + total_small_changes)
##    large_change_prop = total_large_changes / total

##    print(total, no_change_count, total_small_changes, total_large_changes, large_change_pro, large_changes_chamber_ID)

    fig.savefig(f"trough_diagnostics-{set_n}.png")
    hmap.savefig(f"stats_diagnostics-{set_n}.png")

        
