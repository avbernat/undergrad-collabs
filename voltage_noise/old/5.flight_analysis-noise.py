#***************************************************************************************************************************
# FLIGHT ANALYSES FOR MULTIPLE FILES
# Version 7
# Last updated: March 30, 2020
# Authors: (Attisano, et al.), Anastasia Bernat, Meredith Cenzer
#
# Execution Time: 13-20 minutes
#***************************************************************************************************************************

import os
import sys
import csv
import re

import pandas as pd
import numpy as np

import time
start = time.time()

#*************************************************************************************************************
# Process/Purpose: If you don't want a function to print, call blockPrint() before it, and enablePrint() when
#       you want it to continue. If you want to disable all printing, start blocking at the top of the file.
#*************************************************************************************************************

def blockPrint():
    sys.stdout = open(os.devnull, 'w')

def enablePrint():
    sys.stdout = sys.__stdout__

#blockPrint()

#***************************************************************************************************************************
# Creates a time list in which each element represents the occurence of a single peak event.
#***************************************************************************************************************************

def time_list(time, channel):
    time_channel=[]
    for i in range(0, len(channel)):
        if float(channel[i]) == 1.00:
            time_channel.append(float(time[i]))

    return time_channel

#***************************************************************************************************************************
# Creates a list in which each element represents the speed variation between successive peak events.
# The function needs to be modified in order to accommodate the circular flight path distance covered by the insect in flight.
# This depends on the mill's arm radius (i.e. the distance between the tethered insect and the rotational pivot) choosen by
# the user. In the example below the arm radius was set to 17.5cm which corresponds to a 1.0996m circular flight path.
#
# Due to the very low friction of the magnetic bearing, the mill's arm stops rotating some time after the insect ends
# its flying bout. This function includes an optional speed correction loop to account for these additional
# rotations that uses a threshold speed value below which the speed is set to 0. The threshold speed value needs to be
# choosen with care when working with slow flying insects.
#
# The function also automatically accounts for unused or empty channels and for instances in which only one flight
# event occurred.
#***************************************************************************************************************************

def speed_list(time, ch_number):
    ch = str(ch_number)
    speed_t=0
    speed_channel=[]
    speed_channel.append(0)
    if len(time) > 0:
        if len(time) > 2:
            for i in range(1, len(time)):
                if float(time[i]) != float(time[i-1]):
                    speed_t = 0.6283/(float(time[i]) - float(time[i-1]))
                    speed_channel.append(float(speed_t))
                else:
                    speed_channel.append(10)

            #*********************************************************************
            # Optional error correction.
            # Change the threshold speed value accordingly
            # Delete the # at the beginning of line 50-52 to activate the command
            #*********************************************************************
            #######mlc change: uncommented minimum speed threshhold below

            for x in range(0, len(speed_channel)):
                if float(speed_channel[x]) < 0.1:
                    speed_channel[x] = 0

        else:
            print ("Channel ",ch, "has only one peak - impossible to calculate motion stats")
    else:
        print ("Channel ",ch, "is empty")
        
    return speed_channel

#***************************************************************************************************************************
# Calculate distance and average speed. The function corrects for false readings in the voltage signal which are identified
# by speed values higher than a certain threshold. Such threshold value can be modified by the user to account for fast
# flying insects. The function also accounts for very short gaps (7s in the example below) if these occurs between two
# consecutive long and ininterrupted flying bouts. Such gap value can be modified by the user.
#***************************************************************************************************************************

def distance(time, speed):
    distance=0
    average_speed=0
    time_new=[]
    speed_new=[]
    time_new_new=[]
    speed_new_new=[]
    if len(time) > 2:
        for i in range(1, len(speed)):
            if float(speed[i]) > 0 and float(speed[i]) < 1.4: #modify the threshold value accordingly
                time_new.append(float(time[i]))
                speed_new.append(float(speed[i]))
                distance += 0.6283
        if len(time_new) > 2:
            time_new_new.append(time_new[0])
            speed_new_new.append(speed_new[0])
            for ii in range(0, len(time_new)-1):
                if float(time_new[ii+1]) <= float(time_new[ii]) + 7: #the gap value can be changed accordingly
                    time_new_new.append(time_new[ii+1])
                    speed_new_new.append(speed_new[ii+1])
            average_speed = sum(speed_new_new)/len(speed_new_new)
        else:
            print('Cannot calculate distance and average speed')
    else:
        print('Cannot calculate distance and average speed')
    return (time_new_new, speed_new_new, distance, average_speed)  

#***************************************************************************************************************************
# Calculates flight duration of a trial. The function reads all the data, splits the data out as a list of strings (each
# string is a row), retrieves the last line of the data, and gets the first element in the list of strings, which is the
# flight duration. 
#***************************************************************************************************************************
    
def find_time_duration(file_name):
    with open(file_name, "r") as txtfile:
        data = txtfile.readlines()         
        tot_duration = float(data[-1].split(",")[0]) - float(data[0].split(",")[0])

    return float(tot_duration)

#***************************************************************************************************************************
# This function returns duration of the shortest and longest bouts in seconds, entire flight duration in seconds and
# percentage of time spent in flight over time spent at rest. The function also returns the number of flying bouts of a
# specified duration and their respective duration expressed as percentage of the entire time spent in flight. In the example
# below the bouts duration were set at 60-300s, 300-900s, 900-3600s, 3600-14400s and >14400s. The recording time was set at
# 8h (28800s). 
#***************************************************************************************************************************

def flying_bouts(time, speed, ch, tot_duration):
    t_odd = []
    t_even = []
    tot_t = []
    last_time = 0
    diff = 0
    flight_time = 0
    longest_bout = 0
    shortest_bout = 0
    bout_time = []
    fly_time=0 
    flight_60_300=[]
    sum_60_300=0
    flight_300_900=[]
    sum_300_900=0
    flight_900_3600=[]
    sum_900_3600=0
    flight_3600_14400=[]
    sum_3600_14400=0
    flight_14400=[]
    sum_14400=0
    events_300=0
    events_900=0
    events_3600=0
    events_14400=0
    events_more_14400=0
    if len(time) > 2:
        if float(time[1]) < float(time[0]) + 20:
            bout_time.append(time[0])

        #***************************************************************************************************************************
        #creates a list of time values where time gaps are no longer than 20s between consecutive time elements of the list
        #***************************************************************************************************************************
   
        for i in range(0, len(time)-1):
            if float(time[i+1]) >= float(time[i]) + 20:
                bout_time.append(time[i])
                bout_time.append(time[i+1])
     
        if bout_time[-1] != time[-1]:
            bout_time.append(time[-1])

        #***************************************************************************************************************************
        #clean the flying bout time event list from redundant values using set().
        #set() method is used to convert any of the iterable to the distinct element and sorted sequence of iterable elements.
        #***************************************************************************************************************************
    
        for t in range(1, len(bout_time)):
            bout_time = sorted(list(set(bout_time))) 

        #***************************************************************************************************************************
        #calculates the flight descriptive statistics
        #***************************************************************************************************************************
        
        if len(bout_time)%2 != 0:
            last_time = float(bout_time[-1])
            del bout_time[-1]

        t_odd = bout_time[0::2]
        t_even = bout_time[1::2]
        for ii in range(0, len(t_odd)):
            diff = float(t_even[ii]) - float(t_odd[ii])
            tot_t.append(diff)

        if float(last_time) != 0:
            diff = float(last_time) - float(t_even[-1])
            tot_t.append(diff)
        flight_time = sum(float(i) for i in tot_t)
        for index in range(0, len(tot_t)):
            if float(tot_t[index])>60 and float(tot_t[index])<=300:
                flight_60_300.append(float(tot_t[index])/flight_time)
            elif float(tot_t[index])>300 and float(tot_t[index])<=900:
                flight_300_900.append(float(tot_t[index])/flight_time)
            elif float(tot_t[index])>900 and float(tot_t[index])<=3600:
                flight_900_3600.append(float(tot_t[index])/flight_time)
            elif float(tot_t[index])>3600 and float(tot_t[index])<=14400:
                flight_3600_14400.append(float(tot_t[index])/flight_time)
            elif float(tot_t[index])>14400:
                flight_14400.append(float(tot_t[index])/flight_time)
        if len(flight_60_300) > 0:
            sum_60_300=sum(float(a) for a in flight_60_300)
            shortest_bout = float(min(flight_60_300))*flight_time
        if len(flight_300_900) > 0:
            sum_300_900=sum(float(b) for b in flight_300_900)
        if len(flight_900_3600) > 0:
            sum_900_3600=sum(float(c) for c in flight_900_3600)
        if len(flight_3600_14400) > 0:
            sum_3600_14400=sum(float(d) for d in flight_3600_14400)
        if len(flight_14400) > 0:
            sum_14400=sum(float(e) for e in flight_14400)           
        longest_bout = max(tot_t)
        fly_time=flight_time/tot_duration          #total recording time defined by the user 
        events_300=len(flight_60_300)
        events_900=len(flight_300_900)
        events_3600=len(flight_900_3600)
        events_14400=len(flight_3600_14400)
        events_more_14400=len(flight_14400)
    else:
        print('Channel', ch, 'has only one peak - cannot perform calculation')

    return (flight_time, shortest_bout, longest_bout, fly_time, sum_60_300, sum_300_900, sum_900_3600, sum_3600_14400, sum_14400, events_300, events_900, events_3600, events_14400, events_more_14400)       

#***************************************************************************************************************************
# Input: filepath for data file as .csv file
# Output: a list of filenames according to data recordings on which bugs flew "Y" during the trial.
#***************************************************************************************************************************
    
def yes_flew(filepath):
    yes_flew_list = []
    with open(filepath, "r") as data_file:
        reader = csv.DictReader(data_file)
        for row in reader:
                if row["flew"] == "Y":
                    yes_flew_list.append(row["filename"])

    return yes_flew_list

#***************************************************************************************************************************
# This function is used to to clean up the final time and speed variation file for each channel in order to produce
# clearer graphs.   
#***************************************************************************************************************************

def graph(time, speed):
    time_new=[]
    speed_new=[]
    x=0
    y=0
    for i in range(0, len(time)-1):
        if float(time[i+1]) > float(time[i]) + 20:
            time_new.append(time[i])
            speed_new.append(speed[i])
            x=float(time[i]) + 1
            time_new.append(x)
            speed_new.append(0)
            y=float(time[i+1]) -1
            time_new.append(y)
            speed_new.append(0)
        else:
            time_new.append(time[i])
            speed_new.append(speed[i])
    time_new.append(0)
    speed_new.append(0)
    
    return time_new, speed_new

#***************************************************************************************************************************                           
# Input: Datafile path with IDs and filenames of the bugs. Can be modified to check for inconsistencies based on
#           the columns.
# Output: A dictionary where the filename is the key and the values are IDs. As well as additional
#           data entry checks and summaries.
#
# Note that this will need to be changed if the actual files are re-named to match the filenames in the data sorted file.
#***************************************************************************************************************************                           

def get_IDs(filepath):
    ID_data = {} 
    with open(filepath, "r") as data_file:
        reader = csv.DictReader(data_file)
    
        total_bug_count = 0
        filename_count = 0
        no_recording_count = 0
        inconsistency_count = 0
        no_ID_count = 0

        no_recording_warning = 0
        dead_count = 0
        short_wing_count = 0
        count_rest = 0

        for row in reader:
            total_bug_count += 1
            set_num = row["set_number"]
            chamber = row["chamber"]
        
            if row["filename"] != 'NA':
                filename_count += 1
                temp_name = row["filename"]
                cases = temp_name.split("-")[0].split('0')
                set_cases = len(cases)
                ID = row["ID"]
            
                # Checking for Inconsistencies:

                if row["NOTES"] == 'no recording' or row["NOTES"] == 'no recording; paint came off pre-trail':
                    print("NO RECORDING WARNING: File exists BUT bugs did NOT fly. ---------------------")
                    print("ID: " + str(ID) + "    set_number: " + set_num + "    chamber: " + chamber)
                    no_recording_warning += 1
                if ID == '':
                    print("NO ID WARNING: File exists but there is no ID ---------------------")
                    print("ID: " + str(ID) + "    set_number: " + set_num + "    chamber: " + chamber)
                    no_ID_count += 1
                if set_cases == 2:
                    set_name = cases[1]
                elif set_cases == 3:
                    if cases[1] == '':
                        set_name = cases[2]
                    elif cases[2] == '':
                         set_name = cases[1] + '0'
                else:
                    print("WARNING: File exists but its NAME may be written inconsistenly: ")
                    print("ID: " + str(ID) + "    set_number: " + set_num + "    chamber: " + chamber)
                    inconsistency_count += 1
                filename = row["filename"]
                ID_data[filename] = ID

            # Tracking No Recordings - uncomment out as needed
        
            else:
                if row["NOTES"] == 'no recording' or row["NOTES"] == 'no recording; paint came off pre-trail':
                    #print("NO RECORDING: No file b/c bugs did NOT fly. ---------------------")
                    #print("ID: " + str(ID) + "    set_number: " + set_num + "    chamber: " + chamber)
                    no_recording_count += 1
                elif row["died?"] == 'Y':
                    #print("DIED: No file b/c bugs died before could be tested. ---------------------")
                    #print("ID: " + str(ID) + "    set_number: " + set_num + "    chamber: " + chamber)
                    dead_count += 1
                elif row["short-wing?"] == 'Y':
                    #print("SHORT-WING: No file b/c filtered out as a short wing bug. ---------------------")
                    #print("ID: " + str(ID) + "    set_number: " + set_num + "    chamber: " + chamber)
                    short_wing_count += 1
                else:
                    count_rest += 1
                
            #filename = "set" + set_num + temp_name.split("set")[1][3:]
            #ID_dict[filename] = ID

    # Summary
    
    print("WARNING CHECKS -------------------------------------")
    print("Total number of bugs: ", total_bug_count)
    print("Count of bugs with files: ", filename_count)
    print("Count of unwanted 'no recordings': ", no_recording_warning)
    print("Count of inconsistent filenames: ", inconsistency_count)
    print("Count of no ID's: ", no_ID_count)

    print("NO RECORDING COUNTS --------------------------------")
    print("Count of total 'no recordings': ", no_recording_count)
    print("Count of deaths before could make a recording: ", dead_count)
    print("Count of short-wings who were filited out: ", short_wing_count)

    print("CHECK ----------------------------------------------")
    sum_no_recordings = (short_wing_count + dead_count + no_recording_count) + filename_count

    print("Check if the sum of no recordings plus bugs with recordings: " + str(sum_no_recordings) + " is equal to the total number of bugs: " + str(total_bug_count))
    print("If they're the same, this is zero: ", count_rest)

    print("DICTIONARY CHECK -----------------------------------")
    print("Check the length of ID_data: ", len(ID_data))
    #print(ID_data)
    print('\n')

    return ID_data

#********************************************************************************************************************
# Input: Filename as a string. Necessary to do this because some files have IDs in their filename at the end before
#           the '.txt' endstring while other files do not have IDs at the end, so each has to undergo
#           different string manipulations to get the desired channel numbers, channel letters, and IDs.
# Output: re.Match object if the filename does end with a digit. 'None' if the filename does NOT end with a digit. 
#********************************************************************************************************************

def filename_ends_with_digit(filename):
    temp_filename = filename.replace("-", "_")
    match = re.match(r'\w*\d+.txt$', temp_filename)
    
    return match

#************************************************************************************************************
# The flight data file(s) can be called by either defining the complete filepath (for example c:\desktop\recordings
# \filename.txt) or defining a default path in the section "write the path here" that will be automatically
# recalled each time the function is run. In the latter case the user will only need to type the name of
# the .txt or .dat file to process when requested.
#************************************************************************************************************

def cls(): print ("\n" * 100)

cls()
# Autumn 2019
#path = "/Users/anastasiabernat/Desktop/Standardized Peaks Test/"
#data_path = r"/Users/anastasiabernat/Desktop/all_dispersal_data_latest4.csv"

# Winter 2020
path = "/Users/anastasiabernat/Desktop/winter2020_standardized_files/"
data_path = r"/Users/anastasiabernat/Desktop/flight-python-scripts-winter2020/data/all_flight_trials-time-processed-July14.2020.csv"

#row_IDs = get_IDs(data_path) #uncomment this if file does not have the ID in its name 

big_list=[]

print(path)
dir_list = sorted(os.listdir(path))
for file in dir_list:
    if file.startswith("."):
        continue
    filepath = path + str(file)
#    filename = input('File path or file name -> ')
    tot_duration = find_time_duration(filepath)
    input_file = open(filepath, mode="r")
    
    df = pd.read_csv(filepath, sep=",")
    n_rows, n_columns = df.shape
    
    data_list = list(input_file)
    time_column = []
    list_dict=dict()
    peaks1 = []
    peaks2 = []
    peaks3 = []
    peaks4 = []
    #peaks5 = []
    #peaks6 = []
    #peaks7 = []
    #peaks8 = []
    
    for i in range(0, len(data_list)):
        if n_columns == 2:
            raw = data_list[i]
            a,b = raw.split(",") # if >5 channels then a,b,c,d,e,f,g,h,j
            time_column.append(a)
            peaks1.append(b)
        if n_columns > 2:
            raw = data_list[i]
            a,b,c,d,e = raw.split(",") # if >5 channels then a,b,c,d,e,f,g,h,j
            time_column.append(a)
            peaks1.append(b)
            peaks2.append(c)
            peaks3.append(d)
            peaks4.append(e)
            #peaks5.append(f)
            #peaks6.append(g)
            #peaks7.append(h)
            #peaks8.append(j)
            
    if n_columns == 2:
        list_dict[1]=peaks1
    if n_columns > 2:
        list_dict[1]=peaks1
        list_dict[2]=peaks2
        list_dict[3]=peaks3
        list_dict[4]=peaks4
        #list_dict[5]=peaks5
        #list_dict[6]=peaks6
        #list_dict[7]=peaks7
        #list_dict[8]=peaks8

    input_file.close()

    output_data = []
    for i in range(1, len(list_dict)+1):

        row_data = {}

        # Filename String Manipulation: Channel Letters, Channel Numbers, and IDs
        
        if filename_ends_with_digit(file):
            ID = str(file).split("_")[-1].replace(".txt", "")
            row_data["ID"] = ID
            print("ID: ", row_data["ID"])         
            filename = str(file).split("_")[3].replace(".txt", "") + "_" + ID + '.txt'
            row_data['filename'] = filename
            channel_chamber = str(file).split("-")[-1].split("_")[0]
            channel_chamber = re.findall('\d+|\D+', channel_chamber)
            channel_chamber = str(channel_chamber[0]) + "-" + str(channel_chamber[1])
            channel_letter = channel_chamber[0]
            channel_num = channel_chamber[2]
            trial_type = str(file).split("_")[2]
            row_data['trial_type'] = trial_type
            row_data["chamber"] = channel_chamber
            row_data["channel_letter"] = channel_letter
            row_data["channel_num"] = channel_num

        else:
            filename = str(file).split("_")[-1].replace(".txt", "") + str(i)+'.txt'
            row_data['filename'] = filename
            row_data["channel_num"] = i
            channel_letter = str(file).split("_")[-1].split("-")[-1].replace(".txt", "")
            channel_num = str(i)
            row_data["channel_letter"] = channel_letter
            row_data["chamber"] = str(channel_letter) + "-" + str(i)
            
            if filename in row_IDs:
                row_data['ID'] = row_IDs[filename]
                print("ID: ", row_IDs[filename])      
            else:
                print("No matching filename in dict: This results in an empty ID. This means\
                      that either the bug died, paint fell off, it was short-winged or no \
                      bug was actually in the channel but a file (with no data) still exists \
                      for it because the other channels had data in it. ")
                
                row_data['ID'] = "dead/NA"
                      
                ''' I checked all the cases (5 total) that would be considered 'missing'.
                    Each case shows either a bug that died, paint fell off, it was short
                    wing, or no bug was ever placed on the channel. Some have ID's like:
                        147 on set 30 channel A4 - it died
                        406 on set 33 channel B3 - paint fell off
                        26 on set 51 channel B4 - it was short wing (not tested)
                    While others have no bug in the channel so no ID is there. E.g.
                        '' on set 66 channel B4
                        '' on set 8 channel B4
                    To double check - ID checks were made in get_IDs function and
                    all bugs have an ID and all ID's that recorded (not empty) data have
                    a filename.
                '''

        # Calculations and Print Statements
        
        print('CHANNEL ' + channel_num + ' -------------------------------------------')
        time_channel = time_list(time_column, list_dict[i])
        speed_channel = speed_list(time_channel, i)
        time_n, speed_n, dist, av_speed = distance(time_channel, speed_channel)
        fly_time, short_bout, long_bout, flight, fly_to_300, fly_to_900, fly_to_3600, fly_to_14400, fly_more_14400, event_300, event_900, event_3600, event_14400, event_more_14400 = flying_bouts(time_n, speed_n, i, tot_duration)
        print('Average speed channel ' + channel_num + ' -> ' + '%.2f' % av_speed)
        print('Total flight time channel ' + channel_num + ' -> ' + '%.2f' % fly_time)
        print('Distance channel ' + channel_num + ' -> ' + '%.2f' % dist)
        print('Shortest flying bout channel ' + channel_num + ' -> ' + '%.2f' % short_bout)
        print('Longest flying bout channel ' + channel_num + ' -> ' + '%.2f' %long_bout)
        print('This individual spent ' + '%.3f' %flight + ' of its time flying with this composition: ')
        print('  60s-300s = ' + '%.3f' %fly_to_300 + ' with ',event_300, 'events')
        print('  300s-900s = ' + '%.3f' %fly_to_900 + ' with ',event_900, 'events')
        print('  900s-3600s = ' + '%.3f' %fly_to_3600 + ' with ',event_3600, 'events')
        print('  3600s-14400s = ' + '%.3f' %fly_to_14400 + ' with ',event_14400, 'events')
        print('  14400s = ' + '%.3f' %fly_more_14400 + ' with ',event_more_14400, 'events')
        print('\n')
        
        time_graph, speed_graph = graph(time_n, speed_n)

        # Flight Stats:
        
        set_number = str(file).split("_")[3].split("-")[0].split("t0")[-1]

        row_data["set_number"] = set_number
        row_data['average_speed'] = av_speed
        row_data['total_flight_time'] = fly_time 
        row_data['distance'] = dist 
        row_data['shortest_flying_bout'] = short_bout         
        row_data['longest_flying_bout'] = long_bout         
        row_data['portion_flying'] = flight
        row_data['total_duration'] = tot_duration
        row_data['max_speed'] = max(speed_graph)

        output_data.append(row_data) # created a list of dictionaries

        if row_data['ID'] == "dead/NA":
            continue
                    
        big_list.append(row_data)
        
        
##        if filename in yes_flew(data_path):
##            OutputFile=open(r"/Users/anastasiabernat/Desktop/Flight_Analyses/" + filename, "w")
##            for index in range(0, len(time_graph)):
##                OutputFile.write('%.1f' % time_graph[index] + ',' + '%.2f' %speed_graph[index] + '\n')
##            OutputFile.close()
        
##        with open(r"/Users/anastasiabernat/Desktop/flight_stats4/flight_stats-" + str(file).split("_")[-1].replace(".txt", "") + ".csv", "w") as csv_file:
##            writer = csv.DictWriter(csv_file, fieldnames = row_data.keys())
##            writer.writeheader()
##            for row in output_data:
##                writer.writerow(row)

#print(big_list)

# All Flight Stats Summary File

outpath = r"/Users/anastasiabernat/Desktop/"
with open(outpath + "flight_stats_summary_winter2020.csv", "w") as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames = big_list[1].keys())
    writer.writeheader()
    for row in big_list:
        writer.writerow(row)

#************************************************************************************************************
# Time it takes to execute the code.
#************************************************************************************************************

end = time.time()

print("---",(end - start), "seconds ---")
print("---",(end - start) / 60, "mintues ---")



