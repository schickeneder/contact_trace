import sys, csv, math

# - open a CSV file
# - read all lines into memory
# - sort all entries by uptime timestamp (if this gets too big, may need to move that to disk eventually)
# - navigate through the list
#       o for each new location, determine whether the new distance is at least > 3(?) m away
#       o continue through the list and add each newly-seen AP to a tmp list
#       o do this until next movement occurs
#               - compare this new tmp list to the old one and print any additions or subtractions and new distance
#               - (optional/later) compare not just +/- but also thesholds and/or orders
#               - new tmp list becomes old tmp list and repeat

#TODO: what about mobile hotspots
# android location service vs GPS?
# also capture velocity/speed for use in measurement rate?
# need to see that "lost" APs are because signal dropped off, so should be the lowest RSSI of previous "current" list
# if we hash say top 3 with highest RSSI..? or some subset/combination?
# pairwise hashed BSSIDs in order descending RSSI order hash(MAC1|MAC2|timestamp) where RSSI(MAC1) > RSSI(MAC2)
# OR triplets? HASH(MAC1|MAC2|MAC3|timestamp) where RSSI(MAC1) > RSSI(MAC2) > RSSI(MAC3)?
# how often is this order likely to change? do I need to conduct further experiments?
# which performs better on average? two pair or 3 pair? how much more security to we gain by doing that?
# what about hashing all of them above some threshold RSSI? xoring in addition to ordered
# for this case a unique hash would be better, but would the collision-based approach provide better privacy?
time_between_limit = 2000 #milliseconds
distance_between_limit = 0 # meters
R = 6373000.0 # approximate radius of earth in meters
	#Equatorial radius (km)	        6378.137
	#Polar radius (km)               6356.752
	#Volumetric mean radius (km)     6371.000
	# https://nssdc.gsfc.nasa.gov/planetary/factsheet/earthfact.html


# Given a list of keys, finds matches in a file
#  - key_list contains keys or hashes from an individual
#  - test_file contains keys (with group keys) for individual(s) who have "tested positive"
#  - test_file contains a key and group key on each line separated by a colon
def findMatches(key_list,test_file):
    #print("Looking for a match in this group {}".format(key_list))
    with open(test_file, "r") as f_test:
        test_current_group_key = ''
        test_group_count = 0 # number of keys in current test group
        test_group_matches = 0 # number of matching keys in current test group
        for line in f_test:
            current_line_keys = line.strip('\n').split(':')
            if current_line_keys[1] != test_current_group_key: # then this is a new group
                if test_group_matches > 0: # then this is an actual group (not just the start)
                    print("Group {} contains {}/{} matches\n".format(test_current_group_key,
                                                              test_group_matches,test_group_count))
                # reset for new group
                test_group_count = 0
                test_group_matches = 0
                test_current_group_key = current_line_keys[1] # set current group key
            else:
                test_group_count += 1
            if current_line_keys[0] in key_list:
                test_group_matches += 1

    return 0

# will return distance in meters between two sets of GPS coords
def distance_GPS():
    return 4

def calcDistLatLong(coord1, coord2):
    #R = 6373000.0 # approximate radius of earth in meters, between equatorial and mean
    lat1 = math.radians(coord1[0])
    lon1 = math.radians(coord1[1])
    lat2 = math.radians(coord2[0])
    lon2 = math.radians(coord2[1])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    dist = R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    #print("getting distance, returning {}".format(dist))
    return dist

def takeSecond(list):
    return int(list[1])

def sort_file(my_file):
    out_file = "time_sorted.csv"
    entries = []
    with open(my_file, "r", errors="ignore") as f_my:
        try:
            for line in f_my:
                entries.append(tuple(line.strip("\n").split(',')))
            entries.sort(key=takeSecond)
        except:
            print("error on line: "+str(line))

    prev_line = 0
    with open(out_file,"w",newline="") as f_out:
        out_write = csv.writer(f_out, delimiter=",")
        for line in entries:
            if line != prev_line:
                out_write.writerow(line)
                prev_line = line


try:
    assert (len(sys.argv) == 2), "1 file arguments required\n"
except AssertionError as error:
    print("Invalid syntax: "+str(error))
    sys.exit(-1)

print(sys.argv)
my_file = str(sys.argv[1])

sort_file(my_file)
# need to sort order..

with open("time_sorted.csv","r",errors="ignore") as f_my: # some bad chars so need ignore
    print("Opening file {}".format(my_file))
    prev_AP_group = []
    prev_AP_group_RSSI = []
    prev_location = (0, 0)
    prev_location_time = 0
    current_AP_group = []
    current_AP_group_RSSI = []
    current_location = (0,0)
    added_APs = 0
    lost_APs = 0
    common_APs = 0
    AP_change_list = []
    try:
        for line in f_my:
            current_line = line.strip('\n').split(',')
            #print(current_line)
            if current_line[0] == "GPS":
                current_location = (float(current_line[3]), float(current_line[4]))
                distance_between = calcDistLatLong(current_location, prev_location)
                time_between = (int(current_line[1]) - prev_location_time)
            if current_line[0] == "GPS" and time_between > time_between_limit and \
                    distance_between > distance_between_limit:
                prev_location_time = int(current_line[1])
                print("-----------New location, AP diffs---------------")
                print("Current location: {} at time {}".format(current_location,int(current_line[1])))
                print("New APs:--------------")
                for BSSID in current_AP_group:
                    if BSSID not in prev_AP_group:
                        print(BSSID + " " + str(current_AP_group_RSSI[current_AP_group.index(BSSID)]))
                        added_APs += 1
                print("Lost APs:-------------")
                for BSSID in prev_AP_group:
                    if BSSID not in current_AP_group:
                        print(BSSID + " " + str(prev_AP_group_RSSI[prev_AP_group.index(BSSID)]))
                        lost_APs += 1
                print("Common APs:-----------")
                for BSSID in prev_AP_group:
                    if BSSID in current_AP_group:
                        print(BSSID + " " + str(current_AP_group_RSSI[current_AP_group.index(BSSID)]))
                        common_APs += 1
                prev_location = current_location
                prev_AP_group = current_AP_group
                prev_AP_group_RSSI = current_AP_group_RSSI
                AP_change_list.append((common_APs,added_APs,lost_APs, int(distance_between), time_between))
                current_AP_group = []
                current_AP_group_RSSI = []
                common_APs = 0
                added_APs = 0
                lost_APs = 0


            elif current_line[0] == "WIFI":  # it's a new AP measurement, otherwise same GPS loc and we don't care
                BSSID = current_line[3]
                RSSI = current_line[4]
                current_AP_group.append(BSSID)
                current_AP_group_RSSI.append(RSSI)
                #if BSSID not in prev_AP_group:
                #    print("New AP {} found".format(BSSID))

    except Exception as e:
        print("Exception: {}".format(e))
        pass

for item in AP_change_list:
    print(*item)





