import sys, csv, time

# purpose of this program is to convert modified, logged .CSV file to a form used by the other hashing programs.
#
# GPS,5758956,1591925227759,40.68466391,-111.8530831,18.203999
# WIFI,5759657,Sarahsoris,4c:ed:fb:ce:a8:e4,-58
# 3c:b7:4b:b3:1d:87,xfinitywifi,[ESS],1981-02-05 11:38:08,11,-80,40.6743079,-111.8370529,1340.113525390625,15.170000076293945,WIFI

pattern = '%Y-%m-%d %H:%M:%S'

def takeSecond(list):
    return int(list[1])

def sort_file(in_file,out_file):
    print("Sorting inputs..")
    entries = [] # stores sorted contents of file in original format
    with open(in_file, "r", errors="ignore") as f_my:
        try:
            for line in f_my:
                entries.append(tuple(line.strip("\n").split(',')))
            entries.sort(key=takeSecond)
            #print(entries)
        except Exception as e:
            print("error {} in line \'{}\', ignoring ".format(e, str(line)))
            print("Probably appears because of trailing newlines in file")
            pass

    current_location = (0, 0) # gps coords  - GPS,5758956,1591925227759,40.68466391,-111.8530831,18.203999
    gps_time = (0, 0) # (relative ms, epoch ms)
    location_error = 0
    with open(out_file,"w",newline="") as f_out:
        out_write = csv.writer(f_out, delimiter=",")
        for line in entries:
            #print(line)
            current_line = line
            if current_line[0] == "GPS":
                current_location = (current_line[3], current_line[4])
                location_error = current_line[5]
                gps_time = (current_line[1], current_line[2]) # (relative ms, epoch ms)
            else: #it is a WIFI line, write to new format - WIFI,5759657,Sarahsoris,4c:ed:fb:ce:a8:e4,-58
                if current_location != (0, 0) and current_line[0] == "WIFI":
                    try:
                        current_time = int(current_line[1]) - int(gps_time[0]) + int(gps_time[1])
                    except Exception as e:
                        print("Error in current_line {}: {}".format(current_line, e))

                    timestamp = time.strftime(pattern, time.localtime(current_time/1000))

                    # (MAC/BSSID, SSID, .., timestamp, RSSI, lat, lng, alt, location error, label)
                    line_converted = (current_line[3], current_line[2], "[]", timestamp, current_line[4], current_location[0],
                                      current_location[1],"",location_error,"WIFI")
                    out_write.writerow(line_converted)


try:
    assert (len(sys.argv) == 2), "1 file arguments required\n"
    in_file = str(sys.argv[1])
except AssertionError as error:
    print("Invalid syntax: "+str(error))
    sys.exit(-1)

out_file = in_file.split('.')[0] + "_converted.csv"
sort_file(in_file,out_file)

