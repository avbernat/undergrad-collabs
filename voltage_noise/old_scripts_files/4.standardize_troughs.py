import os
import matplotlib.pyplot as plt

def trough_standardization(column, dev_min, dev_max):
    
    #************************************************************************************************************
    #
    # Standardizes the voltage data for each channel by identifying large deviances in voltages as troughs.
    #
    # INPUT:    List of voltage values as floats.
    #
    # PROCESS:  Voltage values are rounded to two decimal places and appended to the volt_column. A confidence
    #           interval is defined around the mean voltage value using a low (min_value) and high (max_value)
    #           threshold. These values can be defined by the user according to the characteristics of the
    #           voltage recording data. Voltages at or higher than the min value of the confidence interval
    #           are set to 0 while voltages far below the min_value are set to 1 and identify the presence
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
    
    print("dev_min is ", dev_min,"    dev_max is ", dev_max)
    for i in range(0, len(column)): 
        volt_column.append(round(column[i], 2))
    
    channel_mean = (sum(volt_column)/len(volt_column))
    min_val=round(channel_mean - dev_min, 2) # * # 0.01 #How min_value is defined--> deviation
    max_val=round(channel_mean + dev_max, 2) # *
 
    for v in range(0, len(volt_column)):  
        x=(volt_column[v]-min_val)/(max_val-min_val) 
        if x < -2:  # *
            int_list.append(1)  
        else:
            int_list.append(0)

    #The if conditional on line 51 looks at the j, j-1, j+1 indices of int_list. 
    #If we start at 0, the first comparison in the loop looks at 0, -1, and 1
    #We should start by comparing 0, 1, and 2. The range should start at 1 instead of 0. 
    for j in range(0, len(int_list)-1): 
        if int_list[j] > int_list[j-1] and int_list[j] >= int_list[j+1]: 
            troughs.append(1)
        else:
            troughs.append(0)

    troughs.append(0)

    print("   Number of 1's:", sum(int_list), "   Number of troughs:", sum(troughs), end=' ')
    
    return troughs 

#************************************************************************************************************
# To call the recording data file, write the complete file directory path. The number of columns processed
# below depends on the number of channels used to record the flight data. For individual insects with only
# two columns per file, only the TBF and voltage reading columns are processed. However, if the number of
# channels is different the script needs to be edited accordingly.
#************************************************************************************************************


username=os.getlogin() # package that talks to operating system
path = f"/Users/{username}/Desktop/Flight_scripts/test_files/"

#path = r"/Users/anastasiabernat/Desktop/Flight_scripts/split_files/"
dir_list = sorted(os.listdir(path))

row = round(len(dir_list)/3)*10
fig, axs = plt.subplots(row,4, figsize=(15, 3*row), facecolor='w', edgecolor='k')
fig.tight_layout(pad=6.0)

print("Files in '", path, "' :")

f=0
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


    #************************************************************************************************************
    # Plot diagnostics to identity noise or files with overly-sensitive troughs. Files with little noise and
    # large troughs will be durable to small changes in deviations. Default here is to test how changes in
    # the min deviation value changes the number of troughs; however, other threshold values such as max
    # deviation and the x value threshold.
    #************************************************************************************************************

    deviations = [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.1]
    row_list=[]
    #volt_dev_max = 0.02
    for volt_dev_min in deviations:
        num_troughs = []
        row={} #{} for dictionaries
        for volt_dev_max in deviations:
            voltage_col = trough_standardization(voltage_column, volt_dev_min, volt_dev_max)
            num_troughs.append(sum(voltage_col))
            print("volt_dev_max is :", volt_dev_max)
        print("volt_dev_min is :", volt_dev_min)
        row_list.append(row)
    
        axs = axs.flatten()
        axs[f].plot(deviations, num_troughs, linestyle='--', marker='o', color='b') # something weird here.
        axs[f].set_ylim([min(num_troughs)-1, max(num_troughs)+1])
        axs[f].title.set_text(file + '\nMax-Min=%i' %(max(num_troughs)-min(num_troughs)))
        axs[f].set_xlabel("min_val Deviation")
        axs[f].set_ylabel("Number of Troughs")
                                                             
        for x,y in zip(deviations, num_troughs):
            label=y
            axs[f].annotate(label,(x,y), textcoords="offset points", xytext=(10,5), ha='center')
        f += 1
    #voltage_col = trough_standardization(voltage_column, volt_dev_min, volt_dev_max)

    #************************************************************************************************************
    # Define the filepath of the output file. Add more channels to the write command line if needed.
    # Also, define the voltage_col with the specific min deviation value argument above if needed. The default
    # here is a min deviation value of - 1 V.
    #************************************************************************************************************
    

    outpath = f"/Users/{username}/Desktop/Flight_scripts/standardized_files/stand_troughs_"

    #outpath = r"/Users/anastasiabernat/Desktop/Flight_scripts/standardized_files/standardized_"
    OutputFile = open(outpath + str(file), mode="w")
    for i in range(0, len(Lines)):
        OutputFile.write('%.2f' % time_column[i] + ", " +
                         '%.2f' % voltage_col[i] + "\n")
    OutputFile.close()

fig.savefig("trough_diagnostic.png") 
