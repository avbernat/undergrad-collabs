summary_list = []

for set_list in sets:

    small_troughs_count = 0
    large_troughs_count = 0
    small_speeds_count = 0
    large_speeds_count = 0
    small_dist_count = 0
    large_dist_count = 0

    large_chamber_troughs = []
    large_chamber_speeds = []
    large_chamber_dist = []

    # trough heat map
    rows = math.ceil(len(set_list) / 5) 
    fig, axes = plt.subplots(rows,5, figsize=(20, 4*rows), facecolor='w', edgecolor='k')
    fig.tight_layout(pad=6.0)

    # speed and distance heat map
    r = rows * 2
    hmap, haxes = plt.subplots(r,5, figsize=(20, 4*r), facecolor='w', edgecolor='k')
    hmap.tight_layout(pad=6.0)

    f=0
    h=0
    
    for file in set_list:

        print("\n", file)
        file_path = path + str(file)
        set_n = file.split("_")[1].split("-")[0]
        
        devs = [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09]
        all_troughs = []
        all_speeds = []
        all_distances = []
       
        for min_dev_val in devs:
            
            print(f"     Calculating...{len(devs)} troughs, speeds, and distances at min dev value of {min_dev_val}")
            troughs = []
            speeds = []
            distances = []
            
            for max_dev_val in devs:
                
                (time_col, trough_col) = standardize(file_path, min_dev_val, max_dev_val, trough_standardization)
                
                blockPrint() # temp
                (avg_speed, total_dist) = analyze(time_col, trough_col, time_list, speed_list, distance)
                enablePrint() # temp
                
                troughs.append(sum(trough_col))
                speeds.append(avg_speed)
                distances.append(total_dist)

            all_troughs.append(troughs)
            all_speeds.append(speeds)
            all_distances.append(distances)
        
        delta_trough = heat_map(devs, f, fig, axes, all_troughs, file, "Number of Troughs")
        f+=1 # spits out the plot_count here which gets updated only if you count
        # then at the end you do file_num - plot count to get the number to delete by with fig.delaxes(axes[1][2])!!!!
        delta_speed = heat_map(devs, h, hmap, haxes, all_speeds, file, "Average Speed (m/s)")
        h+=1
        delta_dist = heat_map(devs, h, hmap, haxes, all_distances, file, "Distance (m/s)")
        h+=1

        dt_small, dt_large, ct_id = get_changes(file, delta_trough, "trough")
        ds_small, ds_large, cs_id = get_changes(file, delta_speed, "speed")
        dd_small, dd_large, cd_id = get_changes(file, delta_dist, "distance")

        total = f

        small_troughs_count += dt_small
        large_troughs_count += dt_large
        small_speeds_count += ds_small
        large_speeds_count += ds_large
        small_dist_count += dd_small
        large_dist_count += dd_large

        large_chamber_troughs.append(ct_id)
        large_chamber_speeds.append(cs_id)
        large_chamber_dist.append(cd_id)

    no_change_troughs = total - (small_troughs_count + large_troughs_count)
    no_change_speeds = total - (small_speeds_count + large_speeds_count)
    no_change_dist = total - (small_dist_count + large_dist_count)

    large_prop_troughs = large_troughs_count / total
    large_prop_speeds = large_speeds_count / total
    large_prop_dist = large_dist_count / total

    d = {"trough": [no_change_troughs, small_troughs_count, large_troughs_count, large_prop_troughs, large_chamber_troughs],
            "speed": [no_change_speeds, small_speeds_count, large_speeds_count, large_prop_speeds, large_chamber_speeds],
            "distance": [no_change_dist, small_dist_count, large_dist_count, large_prop_dist, large_chamber_dist]}
    
    stats = ["trough", "speed", "distance"]
    three_rows = []
    
    for stat in stats:
        
        row_data = {}

        row_data["stat"] = stat
        row_data["set"] = set_n
        row_data["total"] = total
        row_data["no_change"] = d[stat][0]
        row_data["small_changes"] = d[stat][1]
        row_data["large_changes"] = d[stat][2]
        row_data["large_prop"] = d[stat][3]
        row_data["large_cIDs"] = d[stat][4]

        three_rows.append(row_data)

    summary_list.append(three_rows)

    outpath = main_path + "diagnostics/"
    fig.savefig(outpath + f"trough_diagnostic-{set_n}.png")
    hmap.savefig(outpath + f"stats_diagnostics-{set_n}.png")

with open(outpath + "diagnostics_summary.csv", "w") as out_file:
    writer = csv.DictWriter(out_file, fieldnames = summary_list[0][0].keys())
    writer.writeheader()
    for rows in summary_list:
        for row in rows:
            writer.writerow(row)