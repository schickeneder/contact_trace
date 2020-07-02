import sys, math
# purpose of this program is to compare the capture logs grouped by user-defined time intervals
#   - this program naively begins at start of file(s) without regard to time/clock synchronization
#   - can compare against it's own groups within the file, or across all possible groups in two files at a time

time_elem = 1 # represents location of time element in data set
signal = 0 # represents signal type ("WIFI" or "GPS") in data set


#--------------------------------------------------
# TODO: if no matches, e.g. empty vector, will try to divide by zero?
def euclidean_distance(vec1,vec2):
    scale = len(vec1)
    if not scale:
        scale = 1
    return math.sqrt(sum([(a-b) ** 2 for a,b in zip(vec1,vec2)]))

#--------------------------------------------------
# returns a normalized, quantized group consisting of a list of identifiers and values ranging from 0-10
# [(BSSID1,5), (BSSID2,3)..]
def normalize_group(group):
    scale_factor = 10 # scale normalization from 0 to scale_factor
    new_group = []
    #group = [('a', -89), ('b', -60), ('c', -56), ('d', -40), ('e', -70)] # for testing
    max_RSSI = max(group,key = lambda g: g[-1])
    min_RSSI = min(group,key = lambda g: g[-1])
    for item in group:
        # TODO: if there's only one element, will try to divide by zero..
        try:
            tmp_norm = (int(item[-1]) - int(min_RSSI[-1])) / (int(max_RSSI[-1]) - int(min_RSSI[-1]))
        except:
            tmp_norm = -90
        new_group.append((item[0], tmp_norm))

    return new_group

# --------------------------------------------------
def count_normalized_euclidean_match(group1,group2):
    group_intersect = []
    group1_BSSID_RSSI = [(item[3],item[-1]) for item in group1]
    group2_BSSID_RSSI = [(item[3],item[-1]) for item in group2]

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

    tmp = euclidean_distance(tuple(group1_vector),tuple(group2_vector))

    """
    print('\033[95m',group1_BSSID_RSSI_norm)
    print('\033[94m',group2_BSSID_RSSI_norm)
    print('\033[95m',group1_BSSID_RSSI)
    print('\033[94m',group2_BSSID_RSSI)
    print('\033[95m',group1_vector)
    print('\033[94m',group2_vector)
    """
    return tmp #, len(group1_vector)

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

# --------------------------------------------------
def match_groups(groups1,groups2, mode="BSSID"):
    group_count = 0
    match_results = {}
    if mode == "BSSID":
        for group1 in groups1:
            group_count += 1
            matches = []
            num_group_elems = 0
            for group2 in groups2:
                current_matches = count_BSSID_matches(group1,group2)
                matches.append(current_matches)
                num_group_elems += len(group1) # all that *could* have matched
            match_results[group_count] = matches, sum(matches)/num_group_elems
        return match_results
    elif mode == "Euclid":
        for group1 in groups1:
            group_count += 1
            matches = []
            num_group_elems = 0
            for group2 in groups2:
                euclid_dist = count_normalized_euclidean_match(group1,group2)
                matches.append(euclid_dist)
                #num_group_elems += len(group1) # all that *could* have matched
            match_results[group_count] = matches #, sum(matches)/num_group_elems
        return match_results
#--------------------------------------------------
# return the min time, max time of the entries, based on the 2nd element (relative clock offset)
# note: if it seems too big, there may be some odd entries at the end of the file that may need to be removed
def get_time_span(entries, elem = 1):
    try:
        return int(min(entries, key = lambda g: int(g[elem]))[elem]), int(max(entries, key = lambda g: int(g[elem]))[elem])
    except Exception as e:
        print("Exception: {} for entries".format(e))
        sys.exit(-1)

#--------------------------------------------------
def into_groups(entries,step=5000, elem = 1):
    groups = []
    prev_slice = 0
    start, stop = get_time_span(entries, elem)
    #print(start,stop, entries)

    for time_slice in range(start, stop, step):
        group = []
        for entry in entries:
            current_timestamp = int(entry[elem])
            if entry[signal] == "WIFI" and \
                    current_timestamp < time_slice and \
                    current_timestamp > prev_slice and \
                    entry not in group:
                group.append(entry)
        prev_slice = time_slice

        if group:
            groups.append(group)

    return groups

#--------------------------------------------------
# reads in up to two files, sorts based on (default) second element and then returns the two lists
def read_sort_file(file, elem = 1):
    print("Sorting inputs for {}..".format(file))
    entries = [] # stores sorted contents of file in original format and sorts
    with open(file, "r", errors="ignore") as f_my:
        try:
            for line in f_my:
                entries.append(tuple(line.strip("\n").split(',')[:5]))
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
    groups1 = into_groups(entries1,10000,time_elem)
    # second file
    entries2 = read_sort_file(file2, time_elem)
    groups2 = into_groups(entries2,10000,time_elem)
    #print("Self-matching------------------------")
    #match_results = match_groups(groups1,groups1)
    #print(match_results)
    print("BSSID-matching--------------------")
    match_results = match_groups(groups1,groups2, "BSSID")
    print(match_results)
    print("Euclid-matching--------------------")
    match_results = match_groups(groups1,groups2, "Euclid")
    print(match_results)

if __name__ == '__main__':
    main()