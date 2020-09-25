import statistics
import os

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
    format_column = [] # column of voltage values rounded to two decimal places
    new_list=[]
    peaks=[]
    
    for i in range(0, len(column)): #rounds data
        format_column.append(round(column[i], 2))
   
    print(format_column[0:10])

    # Threshold values can be modified accordingly.
    channel_mean = (sum(format_column)/len(format_column))
    min_val=round(channel_mean - 0.01, 2) # The default values are set to deliver a fine tune signal standardization
    max_val=round(channel_mean + 0.02, 2) # This max value is .02 + mean rounded to the second decimal place

    print("mean: ", channel_mean)
    print("min value: ", min_val)
    print("max value: ", max_val)

    for v in range(0, len(format_column)):  
    #finding instances how voltage value compares to min (ie if less than min by a lot)
        x=(format_column[v]-min_val)/(max_val-min_val) 

        #x says how far we are to min relative to how far the max is from the min.

        # Is there a statistical name for x? AB: Yes! Good question, it's called the Minmax normalization
        # or min-max algorithm. When the format_column value is = the max value, x = 1. This means, 
        # the minimum value in X is mapped to 0 and the maximum value in X is mapped to 1. However, overall,
        # we are transforming the data set from one range to a range to another (our voltages can be much
        # much lower than the min value, leading to those high negative values).

        if v == 0 or v == 1: 
            print("x:", x)
            print("numerator:", (format_column[v]-min_val))
            print("denominator:", (max_val-min_val))

        # Peak vs. nonpeak threshold  
        if x < -2:  # used negative 2 a stronger cut off when determining what is a dip in voltage. 
        #If our voltage value twice as far below the min value as the min value is from the max value
            new_list.append(1)  # define as peak
        else:
            new_list.append(0) # not a peak
        
        #tells us when there is a really low value; how do all these zeroes and ones get understood as a peak

        if v == 0 or v==1:
            print("x:", x)
            print("numerator:",format_column[v]-min_val)
            print("denominator:",max_val-min_val)

           
    for j in range(0, len(new_list)-1): 
        # range(1, len(new_list)-1); when we evaluate for i=0, new_list[0 -1]= last element of new list

        vals = f"j = {j}, new_list[{j}] = {new_list[j]}, new_list[{j-1}] = {new_list[j-1]}, new_list[{j+1}] = {new_list[j+1]}"
        print(vals) #tells us for each value the three things we compared to one another 
       
        if new_list[j] > new_list[j-1] and new_list[j] >= new_list[j+1]: 
            peaks.append(1)
            #why don't we start range at 1 and not include line 86? AB: try running and see what happens if you remove the -1 
        else:
            peaks.append(0)
    peaks.append(0)  

    return peaks 

#new_list evaluates whether voltage vlaue is significant or is it very low relative to max to min range 

#************************************************************************************************************
# The flight data file can be called by defining the complete file directory path or defining a default path in
# the section "write the path here" (for example c:\desktop\recordings \filename.txt) that will be automatically
# recalled each time the function is run. In the latter case the user will only need to type the name of
# the .txt or .dat file to process when requested.
#************************************************************************************************************

# Autumn 2019
#path = "/Users/anastasiabernat/Desktop/Flight trials_WinDAQ Recordings_Fall 2019/Text Files/"
#path = "/Users/anastasiabernat/Desktop/odd_text_files/"

#Winter 2020
username=os.getlogin() # package that talks to operating system
path = f"/Users/{username}/Desktop/git_repositories/undergrad-collabs/voltage_noise/test_files/"
print(path)

dir_list = sorted(os.listdir(path))

print("Files and directories in", path, "' :")
    
for file in dir_list:
    if file.startswith("."):
        continue #ignore
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
    folderpath = f"/Users/{username}/Desktop/git_repositories/undergrad-collabs/voltage_noise/standardized_files/standardized_peaks_"
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



