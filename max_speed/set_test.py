import os

main_path = r"/Users/anastasiabernat/Desktop/Dispersal/Trials-Winter2020/"
path = main_path + "split_files/"
dir_list = sorted(os.listdir(path))

max_set_num = int(dir_list[-1].split("_")[1].split("-")[0].split("t0")[-1])

# Rearranging the directory_list into list of files by set. 
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
    sets.append(set_list)


print([sets[15]])