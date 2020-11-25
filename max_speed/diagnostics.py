import os
import csv
import sys
import math
import numpy as np
import matplotlib.pyplot as plt

from standardize_troughs import trough_standardization
from flight_analysis import time_list, speed_list, distance
from flight_analysis import blockPrint, enablePrint

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

def get_changes(file_name, dstat, statistic):

    chamber_ID = None
    dsmall_count = 0
    dlarge_count = 0

    if statistic == "trough" or statistic == "distance":
        if dstat > 0 and dstat < 15: # small change
            dsmall_count = 1
            stat = "trough" 

        if dstat >= 15: # large change
            chamber_ID = file_name.split("-")[-1].split(".")[0]
            dlarge_count = 1

    if statistic == "speed":
        if dstat > 0 and dstat < 0.1: # small change
            dsmall_count = 1
            stat = "trough" 

        if dstat >= 0.1: # large change
            chamber_ID = file_name.split("-")[-1].split(".")[0]
            dlarge_count = 1

    return dsmall_count, dlarge_count, chamber_ID

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

    return delta_stat
    
main_path = r"/Users/anastasiabernat/Desktop/git_repositories/undergrad-collabs/max_speed/"
path = main_path + "test_files/"
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
    if set_list != []:
        sets.append(set_list)

#set_number=15 # choose your set here
#sets = [sets[set_number-1]] 

summary_list = []

for set_list in sets:

    small_troughs_count = 0
    large_troughs_count = 0
    small_speeds_count = 0
    large_speeds_count = 0
    small_dist_count = 0
    large_dist_count = 0

    large_chamber_troughs = []
    large_chamber_speeds = []
    large_chamber_dist = []

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
        
        devs = [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09]
        all_troughs = []
        all_speeds = []
        all_distances = []
        for min_dev_val in devs:
            print(f"     Calculating...{len(devs)} troughs, speeds, and distances at min dev value of {min_dev_val}")
            troughs = []
            speeds = []
            distances = []
            for max_dev_val in devs:
                (time_col, trough_col) = standardize(file_path, min_dev_val, max_dev_val, trough_standardization)
                blockPrint() # temp
                (avg_speed, total_dist) = analyze(time_col, trough_col, time_list, speed_list, distance)
                enablePrint() # temp
                troughs.append(sum(trough_col))
                speeds.append(avg_speed)
                distances.append(total_dist)
            all_troughs.append(troughs)
            all_speeds.append(speeds)
            all_distances.append(distances)
        
        delta_trough = heat_map(devs, f, fig, axes, all_troughs, file, "Number of Troughs")
        f+=1
        delta_speed = heat_map(devs, h, hmap, haxes, all_speeds, file, "Average Speed (m/s)")
        h+=1
        delta_dist = heat_map(devs, h, hmap, haxes, all_distances, file, "Distance (m/s)")
        h+=1

        dt_small, dt_large, ct_id = get_changes(file, delta_trough, "trough")
        ds_small, ds_large, cs_id = get_changes(file, delta_speed, "speed")
        dd_small, dd_large, cd_id = get_changes(file, delta_dist, "distance")

        total = f

        small_troughs_count += dt_small
        large_troughs_count += dt_large
        small_speeds_count += ds_small
        large_speeds_count += ds_large
        small_dist_count += dd_small
        large_dist_count += dd_large

        large_chamber_troughs.append(ct_id)
        large_chamber_speeds.append(cs_id)
        large_chamber_dist.append(cd_id)

    no_change_troughs = total - (small_troughs_count + large_troughs_count)
    no_change_speeds = total - (small_speeds_count + large_speeds_count)
    no_change_dist = total - (small_dist_count + large_dist_count)

    large_prop_troughs = large_troughs_count / total
    large_prop_speeds = large_speeds_count / total
    large_prop_dist = large_dist_count / total

    d = {"trough": [no_change_troughs, small_troughs_count, large_troughs_count, large_prop_troughs, large_chamber_troughs],
            "speed": [no_change_speeds, small_speeds_count, large_speeds_count, large_prop_speeds, large_chamber_speeds],
            "distance": [no_change_dist, small_dist_count, large_dist_count, large_prop_dist, large_chamber_dist]}
    
    stats = ["trough", "speed", "distance"]
    three_rows = []
    
    for stat in stats:
        
        row_data = {}

        row_data["stat"] = stat
        row_data["set"] = set_n
        row_data["total"] = total
        row_data["no_change"] = d[stat][0]
        row_data["small_changes"] = d[stat][1]
        row_data["large_changes"] = d[stat][2]
        row_data["large_prop"] = d[stat][3]
        row_data["large_cIDs"] = d[stat][4]

        three_rows.append(row_data)

    summary_list.append(three_rows)

    outpath = main_path + "diagnostics/"
    fig.savefig(outpath + f"trough_diagnostic-{set_n}.png")
    hmap.savefig(outpath + f"stats_diagnostics-{set_n}.png")

with open(outpath + "diagnostics_summary.csv", "w") as out_file:
    writer = csv.DictWriter(out_file, fieldnames = summary_list[0][0].keys())
    writer.writeheader()
    for rows in summary_list:
        for row in rows:
            writer.writerow(row)
