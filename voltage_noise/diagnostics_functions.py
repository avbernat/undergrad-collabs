import numpy as np

def trough_standardization(column, dev_min, dev_max):
    
    volt_column = [] 
    int_list =[] # sequences of 0s and 1s. 
    troughs=[]
    
    for i in range(0, len(column)): 
        volt_column.append(round(column[i], 2))
    
    channel_mean = (sum(volt_column)/len(volt_column))
    min_val=round(channel_mean - dev_min, 2) # * 
    max_val=round(channel_mean + dev_max, 2) # *
 
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


def time_list(time, channel):
    
    time_channel=[]
    for i in range(0, len(channel)):
        if float(channel[i]) == 1.00:
            time_channel.append(float(time[i]))

    return time_channel


def speed_list(time):
    
    speed_t=0
    speed_channel=[]
    speed_channel.append(0)
    
    if len(time) > 0:
        if len(time) > 2:
            for i in range(1, len(time)):
                if float(time[i]) != float(time[i-1]):
                    speed_t = 0.6283/(float(time[i]) - float(time[i-1])) # *
                    speed_channel.append(float(speed_t))
                else:
                    speed_channel.append(9999) 
            
            for x in range(0, len(speed_channel)): # Optional speed correction.
                if float(speed_channel[x]) < 0.1: 
                    speed_channel[x] = 0

        else:
            print ("Has only one peak - impossible to calculate motion stats")
    else:
        print ("Channel is empty")
        
    return speed_channel


def distance(time, speed):

    distance=0
    average_speed=0
    time_new=[]
    speed_new=[]
    time_final=[]
    speed_final=[]

    if len(time) > 2:
        
        for i in range(1, len(speed)):
            if float(speed[i]) > 0 and float(speed[i]) < 1.4: # Modify the threshold value accordingly
                time_new.append(float(time[i]))
                speed_new.append(float(speed[i]))
                distance += 0.6283

        if len(time_new) > 2:
            time_final.append(time_new[0])
            speed_final.append(speed_new[0])
            for j in range(0, len(time_new)-1):
                if float(time_new[j+1]) - float(time_new[j]) <= 7: # The gap value can be changed accordingly
                    time_final.append(time_new[j+1])
                    speed_final.append(speed_new[j+1])
            average_speed = sum(speed_final)/len(speed_final)
            
        else:
            print('Cannot calculate distance and average speed')
    else:
        print('Cannot calculate distance and average speed')
        
    return (time_final, speed_final, distance, average_speed)  


def heat_map(deviations, f, heat_map, axs, matrix, filename, bar_title):

    a = np.array(matrix)
    axs = axs.flatten()
    im = axs[f].imshow(a, cmap='viridis', interpolation='nearest') # cmap='hot'

    axs[f].title.set_text(filename + '\nMax-Min=%i' %(np.max(matrix)-np.min(matrix)))
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
    
