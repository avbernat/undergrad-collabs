import statistics

#************************************************************************************************************
# This function spits out a list of file names in a given directory. The purpose is to loop through this list
# so as to run this standardization over many files.
#************************************************************************************************************

import os

# Autumn 2019
#path = "/Users/anastasiabernat/Desktop/Flight trials_WinDAQ Recordings_Fall 2019/Text Files/"
#path = "/Users/anastasiabernat/Desktop/odd_text_files/"

#Winter 2020
path = r"/Users/anastasiabernat/Desktop/git_repositories/undergrad-collabs/voltage_noise/noise_txt_files/"
#path = r"/Users/anasilberg/Desktop/voltage_noise/edits/texts/"

dir_list = sorted(os.listdir(path))

print("Files and directories in", path, "' :")
    
#************************************************************************************************************
# This function performs a standardization of the voltage data for each channel. This is achieved by defining a
# **confidence interval** around the mean voltage value using a low (min_val) and high (max_val) threshold. These
# values can be defined by the user according to the characteristics of the voltage recording data. Voltages
# lower than min_val are set to 0 and define the base level. Voltages above max_val are set to 1 and identify
# the presence of a peak. Finally a list of peaks is created.
# INPUT: colum, which is a list of floats that gets rounded to two decimal places and appended to format_colum.
# OUTPUT: peaks, a list of floats. 
#************************************************************************************************************

def peak_standardization(column):
    format_column = [] # column of rounded integers
    new_list=[]
    peaks=[]
    
    for i in range(0, len(column)):
        format_column.append(round(column[i], 2))

    # Threshold values can be modified accordingly.
    channel_mean = (sum(format_column)/len(format_column))
    min_val=round(channel_mean - 0.01, 2) # The default values are set to deliver a fine tune signal standardization
    max_val=round(channel_mean + 0.02, 2) # This max value is .02 + mean rounded to the second decimal place

    for ii in range(0, len(format_column)):
        x=(format_column[ii]-min_val)/(max_val-min_val)
        if x < -2:  # used negative 2 a stronger cut off when determining what is a dip in voltage. ??? -2
            new_list.append(1) 
        else:
            new_list.append(0) 

    for iii in range(0, len(new_list)-1):
        if new_list[iii] > new_list[iii-1] and new_list[iii] >= new_list[iii+1]:
            peaks.append(1)
        else:
            peaks.append(0)
    peaks.append(0)

    return peaks 


#************************************************************************************************************
# The flight data file can be called by either defining the complete filepath (for example c:\desktop\recordings
# \filename.txt) or defining a default path in the section "write the path here" that will be automatically
# recalled each time the function is run. In the latter case the user will only need to type the name of
# the .txt or .dat file to process when requested.
#************************************************************************************************************

for file in dir_list:
    if file.startswith("."):
        continue
    filepath = path + str(file)
    #print(filepath)
#    filename = input("File path -> ")
    InputFile = open(filepath, mode="r", encoding='latin-1')
    
    #************************************************************************************************************
    # The flight recording data is a .csv file in which the first column represents the time of the voltage event,
    # while columns from 2 onwards represent the reading from each data-logger channels. The number of columns to
    # process depends on the number of channels used to record the flight data. The example below is for a case in 
    # which 5 channels were used. If the number of channels is different the script needs to be edited accordingly. 
    #************************************************************************************************************

    Lines = InputFile.readlines()
    time_column = []
    voltage_column = []
    #datetime_column = []
    #third_column = []
    #fourth_column = []
    #fifth_column = []
    #sixth_column = []
    #seventh_column = []
    #eighth_column = []
    for i in range(0, len(Lines)):
        raw = Lines[i]
        a,b,c = raw.split(",") # if > 5 channels then a,b,c,d,e,f,g,h,j
        time_column.append(float(a))
        voltage_column.append(float(b))
        #datetime_column.append(float(c))
        #third_column.append(float(d))
        #fourth_column.append(float(e))
        #fifth_column.append(float(f))
        #sixth_column.append(float(g)) 
        #seventh_column.append(float(h))
        #eighth_column.append(float(j))

    InputFile.close()

    voltage_column = peak_standardization(voltage_column)
    #datetime_column = peak_standardization(datetime_column)
    #third_column = peak_standardization(third_column)
    #fourth_column = peak_standardization(fourth_column)
    #fifth_column = peak_standardization(fifth_column)
    #sixth_column = peak_standardization(sixth_column)
    #seventh_column = peak_standardization(seventh_column)
    #eighth_column = peak_standardization(eighth_column)

    #************************************************************************************************************
    # Define the filepath of the output file. Add more channels to the write command line if needed. 
    #************************************************************************************************************
    
    #folderpath = r"/Users/anasilberg/Desktop/voltage_noise/edits/standardized_files/standardized_peaks_"
    folderpath = r"/Users/anastasiabernat/Desktop/git_repositories/undergrad-collabs/voltage_noise/standardized_files/standardized_peaks_"
    OutputFile = open(folderpath + str(file), mode="w")
    for i in range(0, len(Lines)):
        OutputFile.write('%.2f' % time_column[i] + ", " +
                         '%.2f' % voltage_column[i] + "\n")
                         #", " + '%.2f' % datetime_column[i] +
                         #", " + '%.2f' % third_column[i] + ", " +
                         #'%.2f' % fourth_column[i] + "\n")
                         #+ '%.2f' % fifth_column[i] + ", " + '%.2f' % sixth_column[i] + ", "
                         #+ '%.2f' % seventh_column[i] + ", " + '%.2f' % eighth_column[i] +"\n") 

    OutputFile.close()



