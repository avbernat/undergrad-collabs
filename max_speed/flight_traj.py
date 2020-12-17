import os
import csv
import numpy as np
import matplotlib
import shutil

from os import path
from matplotlib import pyplot as plt
from matplotlib import style

from scipy.interpolate import make_interp_spline, BSpline
from scipy.interpolate import interp1d
from scipy import interpolate

style.use('ggplot')

#******************************************************************************
# Generates a graph or multiple graphs in specified directory. Inputs are text
# files generated by the flight_analysis python script with the first column
# representing time (seconds from the start) and the second column representing
# speed in m/s. the x-axis is time while the y-axis is speed (m/s). The output
# is a graph saved as a .png in a specified directory or folder. 
#******************************************************************************

def color_palette(data_path):

    #**********************************************************************************************
    # Building color palettes based on variables want to graph.
    #
    # Source: https://matplotlib.org/3.2.1/tutorials/colors/colors.html
    #**********************************************************************************************
        
    flight_type_dict = {}
    sex_dict = {}
    pop_dict = {}
    mass_dict = {}
    host_dict = {}

    with open(data_path, "r") as flight_data:
        reader = csv.DictReader(flight_data)
        for row in reader:
            ID = row["ID"]
            set_num = row["set_number"]
            chamber = row["chamber"].split("-")[0] + row["chamber"].split("-")[-1]
            flight_type = row["flight_type"]
            sex = row["sex"]
            pop = row["population"]

            m = row["mass"]
            if m == '':
                m = "0.0"
            mass = float(m)
            
            if (ID, chamber, set_num) not in flight_type_dict:
                flight_type_dict[(ID, chamber, set_num)] = flight_type
                
            if (ID, set_num) not in sex_dict:
                if sex == "F":
                    sex_dict[(ID, set_num)] = "C0"
                if sex == "M":
                    sex_dict[(ID, set_num)] = "C1"
                    
            if (ID, set_num) not in host_dict:
                if pop == "North Key Largo" or pop == "Key Largo" or pop == "Plantation Key":
                    host_dict[(ID, set_num)] = "g"
                else:
                    host_dict[(ID, set_num)] = "b"
                    
            if (ID, set_num) not in pop_dict:
                if pop == "North Key Largo":
                    pop_dict[(ID, set_num)] = "b"
                if pop == "Key Largo":
                    pop_dict[(ID, set_num)] = "g"
                if pop == "Plantation Key":
                    pop_dict[(ID, set_num)] = "w"
                if pop == "Homestead":
                    pop_dict[(ID, set_num)] = "y"
                if pop == "Gainesville":
                    pop_dict[(ID, set_num)] = "k" #'tab:purple'
                if pop == "Lake Wales":
                    pop_dict[(ID, set_num)] = "r"
                if pop == "Lake Placid":
                    pop_dict[(ID, set_num)] = 'tab:orange'
                if pop == "Leesburg":
                    pop_dict[(ID, set_num)] = 'tab:pink'
                    
            if (ID, set_num) not in mass_dict:
                if mass < 0.0527: # 0.05271686 mean of mass, calculated in R
                    mass_dict[(ID, set_num)] = "k"
                if mass >= 0.0527: 
                    mass_dict[(ID, set_num)] = "r"
   
    return flight_type_dict, sex_dict, pop_dict, mass_dict, host_dict

def plot_trajectories(x, y, plt, filename, ID, set_n, chamber, flight_type_dictionary, sex_dictionary, pop_dictionary, 
                                mass_dictionary, host_dictionary, outpath, plot_spline=False, plot_speed=False, 
                                plot_acceleration=False, individual=False):

   #**********************************************************************************************
   # Plotting Summary or Individual Graphs:
   #
   # Spline creation - linear and polynomial.
   #
   #   1. Write 'True' to which Boolean flag method you want to use to create the spline.
   #   2. Write 'True' to plot either speed or acceleration plot. 
   #   3. Write 'True' if want individual file plots.
   #
   # Extra Info:
   # plot derivative: https://stackoverflow.com/questions/52957623/how-to-plot-the-derivative-of-a-plot-python
   # plt.plot(x,y, 'c', linewidth = 0.8)
   #
   # Smooth out the data using splines
   # Smoothing the data: https://stackoverflow.com/questions/5283649/plot-smooth-line-with-pyplot
   #
   # plt.grid(True, color = 'k')
   #***********************************************
   # Final plot features (titles, labels, etc.)
   #***********************************************
   #
   #
   #**********************************************************************************************
   
   # Palettes:
   # sex_color = sex_dictionary[(ID, set_n)]
   # pop_color = pop_dictionary[(ID, set_n)]
   # mass_color = mass_dictionary[(ID, set_n)]
   # host_color = host_dictionary[(ID, set_n)]  

   # Filtering:
   # flight_type = flight_type_dictionary[(ID, chamber, set_n)]
   # if flight_type == "B" or flight_type == "":
   #     continue
    
   # time_duration = seconds_dict[(ID_num, set_num)]
   # if time_duration < 4000:
   #     continue

   initial_time = x[0]
   for i in range(len(x)):
      x[i] = x[i] - initial_time

   x = x[0:len(x)-1]
   y = y[0:len(y)-1]

   if len(x) == 1 or len(x) == 0:  #if x == [0.0] and y == [0.0]: # Skips any files whose only measurements are these.
      plot_spline=False
      plot_speed=False
      plot_acceleration=False
      individual=False
   
            
   if plot_spline: # Linear Spline: (Generates no negatives)
      xnew = np.linspace(min(x), max(x), 20) # last num argument represents number of points to make between x.min and x.max
      x = np.array(x)
      y = np.array(y)
      f = interp1d(x, y) # first order = linear
      #f2 = interp1d(x, y, kind = 'quadratic') # second order = quadratic
      #f3 = interp1d(x, y, kind = 'cubic') # third order = cubic

      plt.plot(x, y, 'c-',
               xnew, f(xnew), 'k-',
               #xnew, f2(xnew), '-',
               #xnew, f3(xnew), '--',
               markersize=1)
      #plt.legend(['data', 'linear', 'quadratic', 'cubic'], loc='best')
      plt.legend(['data', 'linear'], loc='best')
    
    plt.title('Flight Trajectories')
    plt.xlabel('Seconds from start') 

    if individual:
        plt.title('Flight Data' + str(' ') + str(filename))
    if plot_speed:
        plt.ylabel('Speed (m/s)')
    if plot_acceleration:
        plt.ylabel('Acceleration (m/s/s)')

    #input_file.close()

    if individual:
        if plot_speed:
            output_filename = 'speed_' + str(filename).replace(".txt", ".png")
        if plot_acceleration:
            output_filename = 'acc_' + str(filename).replace(".txt", ".png")
        concatenated_path = os.path.join(outpath, output_filename)
        plt.savefig(concatenated_path, dpi=300, bbox_inches='tight')
        plt.clf()

########################################################################################################################

if __name__=="__main__":

    summary_file_path = "/Users/anastasiabernat/Desktop/1.trials-time-processed-Dec10.2020.csv"
    flight_type_dict, sex_dict, pop_dict, mass_dict, host_dict = color_palette(summary_file_path)

    plt.figure()
    path = r"/Users/anastasiabernat/Desktop/Flight_Analyses/"
    dir_list = sorted(os.listdir(path))

    for filename in dir_list:
        if filename.startswith("."):
            continue

        ID_num = str(filename).split("_")[-1].replace(".txt", "")
        set_num = str(filename).split("-")[0].split("t")[-1].lstrip('0')
        chamber = str(filename).split("_")[0].split("-")[-1]
        
        #***********************************************
        # Read each flight analysis file and manipulate
        # its speed (m/s) and time (s) readings.
        #***********************************************
        
        filepath = path + str(filename)
        input_file = open(filepath, mode="r", encoding='latin-1')
        
        x = []
        y = []
        is_initial_start_time = True
        
        for row in input_file:
            split = row.split(',')
            if is_initial_start_time:
                initial_time = float(split[0])
                is_initial_start_time = False
            time = float(split[0]) - initial_time
            speed = float(split[1]) 

    outpath = r'/Users/anastasiabernat/Desktop/Flight_Trajectories/'
    output_filename = "flight_trajectories-20.png"
    concatenated_path = os.path.join(outpath, output_filename)
    plt.savefig(concatenated_path, dpi=300, bbox_inches='tight')
    plt.clf()
    ##plt.show()
