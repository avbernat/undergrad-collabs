
troughs = []
int_list = [0,0,0]

for j in range(0, len(int_list)-1): 
    if int_list[j] > int_list[j-1] and int_list[j] >= int_list[j+1]: 
        troughs.append(1)
    else:
        troughs.append(0)

troughs.append(0)
print(troughs)

#How can different int_lists change the troughs
