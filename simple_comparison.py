import math
import sys
import itertools
import hashlib
from plotter import plot_test
import matplotlib.pyplot as plt


# purpose of this program is to compare the capture logs grouped by user-defined time intervals
# INPUTS: one or two file names for comparison
#   - program imports file(s) and splits observations into groups
#   - if given two files, begins at the start of the first file and matches any synchronized groups from the second file
#   - otherwise if one file, compares against its own groups in an auto-correlation sort of way
#   - plots the results!

time_elem = 1  # represents location of time element in data set (order in .csv format)
signal = 0  # represents signal type ("WIFI" or "GPS") in data set
R = 6373000.0 # approximate radius of earth in meters
	#Equatorial radius (km)	        6378.137
	#Polar radius (km)               6356.752
	#Volumetric mean radius (km)     6371.000
	# https://nssdc.gsfc.nasa.gov/planetary/factsheet/earthfact.html

# We define horizontal accuracy as the radius of 68% confidence. <--android GPS accuracy

# --------------------------------------------------
# Group class --------------------------------------
#  - contains WiFi observations
class Group:
    def __init__(self, slice_size = 5000, group_number = 0):
        self.observations = [] # raw WiFi obs: ('WIFI', '1829260283', 'Walmartwifi', 'c8:00:84:f1:68:af', '-78', '')
        self.hashed_observations = []
        self.lat = 0.0
        self.lon = 0.0
        self.err = 0.0 # radial error in lat/lon measurement
        self.time = 0
        self.gkey = ""
        self.slice_size = slice_size
        self.group_number = group_number

    def add_obs(self, observation):
        self.observations.append(observation)

    def add_loc(self, lat, lon, err, time):
        self.lat = lat
        self.lon = lon
        self.err = err
        self.time = time

    # this should compute a group key based on the private_key and (hashed?) observations
    def compute_gkey(self, private_key):
        self.gkey = "temporary"

    def compute_weak_hashed(self):
        pass

    #doesn't seem to work that well
    def compute_pair_hashes(self):
        self.hashed_observations = []
        self.observations.sort(key=lambda x: int(x[4]), reverse=True)
        prev = 0
        for obs in self.observations:
            #print(obs)
            if prev:
                obs_as_string = str(prev[2]) + str(prev[3]) + str(obs[2]) + str(obs[3])
                #print(obs_as_string)
                hashed = hashlib.md5(obs_as_string.encode()).hexdigest()
                self.hashed_observations.append(hashed)
            prev = obs

        #print(len(self.observations), len(self.hashed_observations))


    #TODO: only works for n choose 2 currently, need to generalize..
    # this doesn't work because it deviates from the original match factor too much
    def compute_multi_hashed(self,n=7,k=2): # as in "n choose k"
        self.observations.sort(key=lambda x: int(x[time_elem]))
        n = min(len(self.observations), n)
        for comb in itertools.combinations(self.observations[n-1::-1], k):
            sorted_comb = (sorted(comb, reverse=True, key=lambda x: int(x[4]))) # descending order
            first = list(sorted_comb[0])
            second = list(sorted_comb[1])
            del first[-1]
            del second[-1]
            obs_as_string = str(''.join(map(str, first)) + str(''.join(map(str, second)))
                                + str(self.time//self.slice_size))
            #print(obs_as_string) # now it's a long string
            hashed = hashlib.md5(obs_as_string.encode()).hexdigest()
            self.hashed_observations.append(hashed)


    def return_timespan(self):
        # returns the max-min of observation timestamps
        pass

    # returns timestamp of first and last observations
    def get_times(self):
        return min(self.observations, key=lambda g: g[1]), max(self.observations, key=lambda g: g[1])

# end Group class --------------------------------------


# --------------------------------------------------
def euclidean_distance(vec1, vec2):
    return math.sqrt(sum([(a - b) ** 2 for a, b in zip(vec1, vec2)]))


# --------------------------------------------------
def manhattan_distance(vec1, vec2):
    return sum([abs(a - b) for a, b in zip(vec1, vec2)])

# --------------------------------------------------
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
    return dist

def normalize_RSSI(RSSI, max, min, steps):
    pass

# --------------------------------------------------
# returns a normalized, quantized group consisting of a list of identifiers and values ranging from 0-10
# [(BSSID1,5), (BSSID2,3)..]
def normalize_group(group):
    scale_factor = 10  # scale normalization from 0 to scale_factor
    new_group = []
    # group = [('a', -89), ('b', -60), ('c', -56), ('d', -40), ('e', -70)] # for testing
    max_RSSI = ("max", -20)  # max(group,key = lambda g: g[-1])
    min_RSSI = ("min", -90)  # min(group,key = lambda g: g[-1])
    for item in group:
        try:
            tmp_norm = (int(item[-1]) - int(min_RSSI[-1])) / (int(max_RSSI[-1]) - int(min_RSSI[-1]))
            new_group.append((item[0], tmp_norm))
        except Exception as e:
            print("Exception in normalize_group {}".format(e), item)
            pass

    return new_group


# --------------------------------------------------
# here group1, group2 are list of observations, not group class
# returns list euclidean and manhattan distances (L1, L2 norms)
# TODO: fix this
def match_distances(observations1, observations2):
    group_intersect = []

    group1_BSSID_RSSI = [(item[3], item[4]) for item in observations1]
    group2_BSSID_RSSI = [(item[3], item[4]) for item in observations2]

    group1_BSSID_RSSI_norm = normalize_group(group1_BSSID_RSSI)
    group2_BSSID_RSSI_norm = normalize_group(group2_BSSID_RSSI)

    group1_vector = []
    group2_vector = []
    for item1 in group1_BSSID_RSSI_norm:
        for item2 in group2_BSSID_RSSI_norm:
            if item1[0] == item2[0]:
                group_intersect.append(item1[0])
                group1_vector.append(item1[-1])
                group2_vector.append(item2[-1])
                break

    tmp = euclidean_distance(tuple(group1_vector), tuple(group2_vector))
    tmp2 = manhattan_distance(tuple(group1_vector), tuple(group2_vector))
    """
    print('\033[95m',group1_BSSID_RSSI_norm)
    print('\033[94m',group2_BSSID_RSSI_norm)
    print('\033[95m',group1_BSSID_RSSI)
    print('\033[94m',group2_BSSID_RSSI)
    print('\033[95m',group1_vector)
    print('\033[94m',group2_vector)
    """
    return tmp, tmp2, len(group1_vector)


# --------------------------------------------------
# returns the number of matches for BSSID/MAC between groups (e.g. size of the intersect)
# added option to match based on RSSI difference
def count_BSSID_matches(group1, group2):
    group_intersect = []
    group1_BSSID_RSSI = [(item[3], item[-1]) for item in group1]
    group2_BSSID_RSSI = [(item[3], item[-1]) for item in group2]
    for item1 in group1_BSSID_RSSI:
        for item2 in group2_BSSID_RSSI:
            if item1[0] == item2[0]:
                group_intersect.append(item1[0])
                break
    return len(group_intersect)


def match_hashes(hobservations1, hobservations2):
    intersect_count = 0
    for item1 in hobservations1:
        for item2 in hobservations2:
            if item1 == item2:
                #print("{} equals {}".format(item1,item2))
                intersect_count += 1
                break
    return intersect_count,len(hobservations1)



# --------------------------------------------------
# TODO: add the coordinates stuff here..
def match_groups(groups1, groups2):
    group_count = 0
    match_results = {}
    for group1 in groups1:
        observations1 = group1.observations
        group1.compute_pair_hashes()
        hobservations1 = group1.hashed_observations

        group_count += 1
        matches = []
        num_group_elems = 0
        for group2 in groups2:
            observations2 = group2.observations
            group2.compute_pair_hashes()
            hobservations2 = group2.hashed_observations
            # current_matches,possible_matches = count_BSSID_matches(group1, group2)
            possible_matches = len(observations1)
            hashed_matches, possible_hash_matches = match_hashes(hobservations1, hobservations2)
            euclid_dist, man_dist, dim = match_distances(observations1, observations2)
            GPS_dist = calcDistLatLong((group1.lat,group1.lon),(group2.lat,group2.lon))

            if dim:
                matches.append((euclid_dist / math.sqrt(dim), man_dist / dim, GPS_dist, dim, possible_matches,
                                group1.err, group2.err, group2.time, hashed_matches / possible_hash_matches))
            else:
                matches.append((2, 2, GPS_dist, dim, possible_matches,
                                group1.err, group2.err, group2.time, hashed_matches / possible_hash_matches)) # just placeholders in case something wrong

            num_group_elems += len(observations1)  # all that *could* have matched
            #print("dim/possible: {}/{}, {} hash matches: {}/{}, {}"
            #      .format(dim, possible_matches, dim/possible_matches, hashed_matches, possible_hash_matches, hashed_matches/possible_hash_matches))
        match_results[group_count] = matches, sum([match[1] for match in matches]) / num_group_elems
    return match_results

# --------------------------------------------------
# attempts a synchronous match between two different groups
#   - for each group in groups1, find a group in groups2 approx matching the time of the first group, compare
#   - offset allows some +/- with differences in timing between groups
def match_groups_synchronous(groups1, groups2, offset):
    matches = []
    for group1 in groups1:
        observations1 = group1.observations
        num_group_elems = 0
        for group2 in groups2:
            if group1.time < group2.time + offset and group1.time > group2.time - offset:
                observations2 = group2.observations
                # current_matches,possible_matches = count_BSSID_matches(group1, group2)
                possible_matches = len(observations1)
                euclid_dist, man_dist, dim = match_distances(observations1, observations2)
                GPS_dist = calcDistLatLong((group1.lat, group1.lon), (group2.lat, group2.lon))

                if dim:
                    matches.append((euclid_dist / math.sqrt(dim), man_dist / dim, GPS_dist, dim, possible_matches,
                                    group1.err, group2.err, group2.time))
                else:
                    matches.append((2, 2, GPS_dist, dim, possible_matches,
                                    group1.err, group2.err, group2.time)) # just placeholders in case something wrong

                num_group_elems += len(observations1)  # all that *could* have matched

    return matches, 0#sum([match[1] for match in matches]) / num_group_elems


# --------------------------------------------------
# return the min time, max time of the entries, based on the 2nd element (relative clock offset)
# note: if it seems too big, there may be some odd entries at the end of the file that may need to be removed
def get_time_span(entries, elem=1):
    try:
        return int(min(entries, key=lambda g: int(g[elem]))[elem]), int(max(entries, key=lambda g: int(g[elem]))[elem])
    except Exception as e:
        print("Exception: {} for entries".format(e))
        sys.exit(-1)


# --------------------------------------------------
# TODO: only replace GPS location with a newer one with less error
# Note: keeps GPS coordinate with lowest error..
def into_groups(entries, step=5000, elem=1):
    groups = []
    prev_slice = 0
    start, stop = get_time_span(entries, elem)
    num_groups = 0

    # split WiFi measurements into groups of equally-spaced time steps
    for time_slice in range(start, stop, step):
        group = Group(slice_size = step, group_number = num_groups)
        lat, lon, err = 0.0, 0.0, 50.0 # zero out GPS to get a new coordinate
        for entry in entries:
            current_timestamp = int(entry[elem])
            if entry[signal] == "WIFI" and \
                    current_timestamp < time_slice and \
                    current_timestamp > prev_slice and \
                    entry not in group.observations:
                group.add_obs(entry)
            elif entry[signal] == "GPS" and \
                    current_timestamp < time_slice and \
                    current_timestamp > prev_slice:
                if float(entry[5]) < err:
                    group.add_loc(lat=float(entry[3]), lon=float(entry[4]), err=float(entry[5]), time=int(entry[2]))
                    err = float(entry[5]) # replace with better coordinate with lower error
        prev_slice = time_slice

        if group.observations and group.time: # only want to add it if time and observations are present
            groups.append(group)
            num_groups += 1

    return groups


# --------------------------------------------------
# reads in up to two files, sorts based on (default) second element and then returns the two lists
def read_sort_file(file, elem=1):
    print("Sorting inputs for {}..".format(file))
    entries = []  # stores sorted contents of file in original format and sorts
    with open(file, "r", errors="ignore") as f_my:
        try:
            for line in f_my:
                split_line = line.strip("\n").strip(",").split(',')
                num_fields = len(split_line)
                # have to add this because SSID's with a "," screwed it up, adding an additional field in the split
                if num_fields == 5 and split_line[0] == "WIFI" or num_fields == 6 and split_line[0] == "GPS":
                    entries.append(tuple(line.strip("\n").split(',')[:6]))
            entries.sort(key=lambda k: int(k[elem]))
        except Exception as e:
            print("error {} in line \'{}\', ignoring ".format(e, str(line)))
            print("Probably appears because of trailing newlines in file")
            pass
    return entries


# ===========================================================================
# ===========================================================================

def main():
    try:
        assert (len(sys.argv) >= 2), "at least 1 file arguments required\n"
        file1 = str(sys.argv[1])
        try:
            file2 = str(sys.argv[2])
        except:
            file2 = 0
            pass

    except AssertionError as error:
        print("Invalid syntax: " + str(error))
        sys.exit(-1)

    # first file
    entries1 = read_sort_file(file1, time_elem)
    groups1 = into_groups(entries1, 5000, time_elem)

    groups1[0].compute_pair_hashes()

    # second file
    if file2: # then match the two files
        entries2 = read_sort_file(file2, time_elem)
        groups2 = into_groups(entries2, 5000, time_elem)

        match_results, _ = match_groups_synchronous(groups1, groups2, 3000)
        output_results = []
        for item in match_results:
            try:
                output_results.append([item[0], item[1], item[2], item[3] / item[4], item[5], item[6], item[7]])
            except Exception as e:
                print("error {} in output_results with item {}".format(e, item))
        plot_test(output_results, "Close Proximity")
        plt.show()

    else: # we do the auto-correlation operation

        print("Euclid-matching--------------------")
        #      (euclid_dist / math.sqrt(dim), man_dist / dim, GPS_dist, dim, possible_matches, group1.err, group2.err, time)
        match_results = match_groups(groups1, groups1)
        output_results = []

        # for self-matching/auto-correlation
        for row in range(1,len(match_results)):
            for item in match_results[row][0]:
                try:
                    output_results.append([item[0], item[1], item[2], item[3] / item[4], item[5], item[6], item[7], item[8]])
                    #print(output_results[-1])
                except Exception as e:
                    print("error {} in output_results with item {}".format(e,item))
            plot_test(output_results, "Indoor Residence")
            output_results = []
        plt.show()

    """
    match_results, _ = match_groups_synchronous(groups1, groups2, 3000)
    output_results = []
    for item in match_results:
        try:
            output_results.append([item[0], item[1], item[2], item[3] / item[4], item[5], item[6], item[7]])
        except Exception as e:
            print("error {} in output_results with item {}".format(e, item))
    plot_test(output_results, "Close Proximity")
    plt.show()
    """
    #for row in output_results:
    #    print(row)
    # print("*************************************************")
    # print(match_results[2])

    """
    percentages = [item[-1] for item in match_results.items()]
    for item in percentages[0]:
        try:
            print(item[0]/math.sqrt(item[1]))
        except:
            print(item[0])
    """
    # print(percentages)
    # percentages = [[subitem[0]/math.sqrt(subitem[1]) for subitem in item if subitem[1] and subitem[0]] for item in percentages]
    # both = [sum(item)/len(item) for item in percentages if len(item)]
    # print(both,sum(both)/len(both))
    # print(percentages)


if __name__ == '__main__':
    main()
