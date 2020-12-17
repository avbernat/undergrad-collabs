import os
import csv
import shutil
import matplotlib

import numpy as np
from matplotlib import style
from matplotlib import pyplot as plt

from scipy.interpolate import make_interp_spline, BSpline
from scipy.interpolate import interp1d
from scipy import interpolate

plt.style.use('ggplot')

def color_palette(data_path):

   #**********************************************************************************************
   #
   # Builds intentional color palettes for categorical groups within the data.
   #
   # INPUT:    A path, data_path, as a string that leads to a file with ID, set number, chamber, 
   #           flight type, sex, population, mass, and host plant columns. 
   #
   # PROCESS:  Generates dictionaries of each categorical group using csv.DictReader where keys
   #           are unique bug identifies (e.g. ID, set number, and chamber) and values are colors
   #           legible to matplotlib plot objects. In this sense, each dictionary becomes a 
   #           'palette' where specific colors can be referenced to corresponding flight 
   #           trajectories. 
   #
   # OUTPUT:   'Palettes,' which are the dictionaries, are returned. 
   #
   # SOURCE:   https://matplotlib.org/3.2.1/tutorials/colors/colors.html
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
   # 
   # Plots either individual flight trajectories or a single graph of all flight trajectories.
   #
   # INPUT:    x, which represents time (s) and y, which represents speed (m/s). plt is the plot
   #           object, filename as a string, ID, set_n, chamber, and dictionaries for palette 
   #           retrieval, outpath for storing graphs, and booleans of plot_spline, plot_speed,
   #           plot_acceleration, and individual.
   #
   # PROCESS:  Booleans determine what graph(s) are generated. 
   #              1. Write 'True' for plot_spline for spline creation - linear or polynomial.
   #              2. Write 'True' to plot either speed or acceleration. 
   #              3. Write 'True' if want individual file plots.
   #           Plots features (titles, labels, etc.)
   #
   # OUTPUT:   Individual flight trajectory plots (.png) are generated.
   #
   # SOURCE:   Smoothing the data: https://stackoverflow.com/questions/5283649/plot-smooth-line-with-pyplot.
   #           Plot derivative: https://stackoverflow.com/questions/52957623/how-to-plot-the-derivative-of-a-plot-python
   #
   #**********************************************************************************************
   
   # Palettes:
   # sex_color = sex_dictionary[(ID, set_n)]
   # pop_color = pop_dictionary[(ID, set_n)]
   # mass_color = mass_dictionary[(ID, set_n)]
   # host_color = host_dictionary[(ID, set_n)]  

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
      if individual:
         plt.plot(x, y, 'c-',
                  xnew, f(xnew), 'k-',
                  #xnew, f2(xnew), 'k--',
                  #xnew, f3(xnew), 'r--',
                  markersize=1)
         #plt.legend(['data', 'linear', 'quadratic', 'cubic'], loc='best')
         plt.legend(['data', 'linear'], loc='best')
      
      plt.plot(xnew, f(xnew), 'k-', markersize=1, linewidth=0.35)
      plt.legend(['linear'], loc='best')
    
   plt.title('Flight Trajectories')
   plt.xlabel('Seconds from start') 

   if individual:
      plt.title('Flight Data' + str(' ') + str(filename))
   if plot_speed:
      plt.ylabel('Speed (m/s)')
   if plot_acceleration:
      plt.ylabel('Acceleration (m/s/s)')

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
   root_path = r"/Users/anastasiabernat/Desktop/Dispersal/Trials-Winter2020/"

   summary_file_path = root_path + "1.trials-time-processed-Dec10.2020.csv"
   flight_type_dict, sex_dict, pop_dict, mass_dict, host_dict = color_palette(summary_file_path)

   plt.figure()
   path = root_path = "flight_analyses/"
   dir_list = sorted(os.listdir(path))

   for filename in dir_list:
      ID_num = str(filename).split("_")[-1].replace(".txt", "")
      set_num = str(filename).split("-")[0].split("t")[-1].lstrip('0')
      chamber = str(filename).split("_")[0].split("-")[-1]

      filepath = path + filename
      input_file = open(filepath, mode="r", encoding='latin-1')
      
      times = []
      speeds = []
      for row in input_file:
         split = row.split(',')
         time = float(split[0])
         speed = float(split[1]) 
         times.append(time)
         speeds.append(speed)

   outfile = root_path + "flight_trajectories-2.png"
   plt.savefig(outpath + outfile, dpi=300, bbox_inches='tight')
   plt.clf()
