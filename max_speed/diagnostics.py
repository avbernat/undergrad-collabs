import os
import math
import matplotlib.pyplot as plt

from standardize_troughs import trough_standardization
from diagnostics_functions import heat_map
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

main_path = r"/Users/anastasiabernat/Desktop/git_repositories/undergrad-collabs/max_speed/" 
path = main_path + "txt_files/"
dir_list = sorted(os.listdir(path))

rows = math.ceil(len(dir_list) / 5) * 2
hmap, axes = plt.subplots(rows,5, figsize=(20, 4*rows), facecolor='w', edgecolor='k')
hmap.tight_layout(pad=6.0)

f=0
for file in dir_list:
    
    print("\n", file)
    file_path = path + str(file)
    
    devs = [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10]
    all_speeds = []
    all_distances = []
    for min_dev_val in devs:
        speeds = []
        distances = []
        for max_dev_val in devs:
            (time_col, trough_col) = standardize(file_path, min_dev_val, max_dev_val, trough_standardization)
            (avg_speed, total_dist) = analyze(time_col, trough_col, time_list, speed_list, distance)
            speeds.append(avg_speed)
            distances.append(total_dist)
        all_speeds.append(speeds)
        all_distances.append(distances)
        
    heat_map(devs, f, hmap, axes, all_speeds, file, "Average Speed (m/s)")
    f+=1
    heat_map(devs, f, hmap, axes, all_distances, file, "Distance (m/s)")
    f+=1

hmap.savefig("stats_diagnostics.png")

    
