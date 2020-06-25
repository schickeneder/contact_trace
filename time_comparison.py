import sys, csv, math

# purpose of this program is to compare the capture logs grouped by user-defined time intervals and vary the offset
# to find the optimal synchronization based on visible APs rather than GPS, indicating a best case matching scenario

# TODO:
#   -group only those with RSSI > N
#   -group only top 50% of APs by RSSI
#   -group only bottom 50% (or 20%?) of APs by RSSI - idea being that those will drop out quicker
#   -group onl thos with RSSI < N - similar idea as above, see which performs better..
#   -maybe split into two groups, top 50% for general area, bottom x% for finer resolution?
#   -which results create more unique per group?

# currently uses the newer format..
pattern = '%Y-%m-%d %H:%M:%S'
RSSI_difference = 0
RSSI_threshold = -70
RSSI_threshold_greater = False # filter AP measurements greater than -70 dbm
RSSI_threshold_less = False # similarly, filter AP measurements less than RSSI_threshold
RSSI_difference_enabled = False # match based on differences in RSSI threshold LTE RSSI difference

#--------------------------------------------------
# Used in sorting function based on second element
# TODO: replace this with a lambda function
def takeSecond(list):
    return int(list[1])

#--------------------------------------------------
# return the longer time span of each of the file entries, based on the 2nd element (relative clock offset)
# note: if it seems too big, there may be some odd entries at the end of the file that may need to be removed
def get_longest_time_span(entries1,entries2):
    try:
        return max((int(entries1[-1][1])-int(entries1[0][1])), (int(entries2[-1][1])-int(entries2[0][1])))
    except Exception as e:
        print("Exception: {} for entries".format(e))
        sys.exit(-1)

#--------------------------------------------------
# returns the number of matches for BSSID/MAC between groups (e.g. size of the intersect)
# added option to match based on RSSI difference
def count_BSSID_matches(group1, group2):
    group_intersect = []
    group1_BSSID_RSSI = [(item[3],item[-1]) for item in group1]
    group2_BSSID_RSSI = [(item[3],item[-1]) for item in group2]
    for item1 in group1_BSSID_RSSI:
        for item2 in group2_BSSID_RSSI:
            if item1[0] == item2[0] and (not RSSI_difference_enabled or abs(int(item1[1])-int(item2[1])) <= RSSI_difference):
                group_intersect.append(item1[0])
                break
    return len(group_intersect)

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
            tmp_norm = 10
        new_group.append((item[0], round(tmp_norm * scale_factor)))

    return new_group

#--------------------------------------------------
# TODO: if no matches, e.g. empty vector, will try to divide by zero?
def euclidean_distance(vec1,vec2):
    return math.sqrt(sum([(a-b) ** 2 for a,b in zip(vec1,vec2)]))

#--------------------------------------------------
# an alternative matching variant:
#   -identify the intersect set of visible APs between two groups
#   -for each group, normalize and discretize RSSI values between 0-10
#   -treating each group as a vector, calculate the euclidean distance between the two groups
#   -return this distance
#
#   this should somewhat compensate for differences in RSSI between different devices
#   TODO: should it be a straight normalization or simple a ranked from 0-10? May need to test both
#        o normalize based on those in the intersect set or normalize each separately before?

#   first will try normalizing 0-10 for those in the intersect set
#   then maybe try ranking 0->N based on order of measurements for each set in the intersect group
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

    print('\033[95m',group1_BSSID_RSSI_norm)
    print('\033[94m',group2_BSSID_RSSI_norm)
    print('\033[95m',group1_BSSID_RSSI)
    print('\033[94m',group2_BSSID_RSSI)
    print('\033[95m',group1_vector)
    print('\033[94m',group2_vector)
    return tmp


# --------------------------------------------------
# performs a varied time comparison with different groupings, ignores GPS entries except for initial
# assumes entries are already ordered based on element[1] (relative time)
#   entries represent the stored capture logs read from riles
#   duration represents the time interval defining a group of APs (in ms)
#   defined_offset is the adjusted timestamp offset between the two capture files, in ms added to file2 (in ms)
#       returns the number of matches after comparing
def time_compare(entries1, entries2, step=5000, defined_offset=0):
    total_matches = 0 # over all groups
    total_min_group = 0 # sum(for all groups min(size(group1),size(group2))
    average_matches = 0 # per group
    total_group_discrepancy = 0 # defined as sum(abs(size(group1)-size(group2)) for all groups)
    number_of_groups = 0 # how many groups/steps do we have?
    file1_time_anchor = (0,0) # relative time ms, epoch time ms
    file2_time_anchor = (0,0)
    total_euclid_distance = 0
    # start the first group with timestamp of first entry from file1, this must be done with GPS
    for entry1 in entries1:
        if entry1[0] == "GPS":
            file1_time_anchor = (int(entry1[1]), int(entry1[2]))
            break
    for entry2 in entries2:
        if entry2[0] == "GPS":
            file2_time_anchor = (int(entry2[1]), int(entry2[2]))
            break
    # determine offsets of relative clock offset between two files, add to 2nd file to synch
    offset = ((file2_time_anchor[1] - file1_time_anchor[1]) - (file2_time_anchor[0] - file1_time_anchor[0]))
    offset += defined_offset # add the user defined offset

    time_span = get_longest_time_span(entries1,entries2)
    #print(time_span, step)

    group1 = []
    group2 = []
    prev_slice = 0
    for time_slice in range(file1_time_anchor[0],(file1_time_anchor[0]+time_span),step):
        #print(time_slice)
        for entry in entries1:
            current_timestamp = int(entry[1])
            if entry[0] == "WIFI" and \
                    current_timestamp < time_slice and \
                    current_timestamp > prev_slice and \
                    (not RSSI_threshold_greater or int(entry[-1]) > RSSI_threshold) and \
                    (not RSSI_threshold_less or int(entry[-1]) < RSSI_threshold) and \
                    entry not in group1:
                group1.append(entry)
        for entry in entries2:
            current_timestamp = int(entry[1])+offset
            if entry[0] == "WIFI" and current_timestamp < time_slice and current_timestamp > prev_slice and \
                    (not RSSI_threshold_greater or int(entry[-1]) > RSSI_threshold) and \
                    (not RSSI_threshold_less or int(entry[-1]) < RSSI_threshold) and \
                    entry not in group2:
                group2.append(entry)

        # metrics.. but only count if two groups are present, e.g. a scan was performed during that time step
        if group1 and group2:
            current_matches = count_BSSID_matches(group1,group2)
            current_euclid_distance = count_normalized_euclidean_match(group1,group2)
            print(current_euclid_distance)
            #print("Group1,Group2, matches: {},{},{}".format(len(group1),len(group2),current_matches))
            total_min_group += min(len(group1), len(group2))
            total_matches += current_matches
            total_group_discrepancy += abs(len(group1)-len(group2))
            total_euclid_distance += current_euclid_distance
            number_of_groups += 1

        # get ready to start next group
        group1 = []
        group2 = []
        prev_slice = time_slice

    # report final numbers
    """
    print("Summary---------------------------------------------")
    print("Step size: {} ms".format(step))
    print("Original offset, defined offset : {},{}".format((offset-defined_offset), defined_offset))
    print("Total Matches / Possible: {}/{}".format(total_matches,total_min_group))
    print("Average Match Percentage: {}".format(total_matches/total_min_group))
    print("Total Group Discrepancy / Number of Groups: {}/{}".format(total_group_discrepancy,number_of_groups))
    print("Average Group Discrepancy: {}".format(total_group_discrepancy/number_of_groups))
    """
    # abbreviated, for file output
    #print("{},{},{}".format(step,defined_offset,total_matches/total_min_group))
    with open(outfile,"a",newline="") as f_out:
        out_write = csv.writer(f_out, delimiter=",")
        out_write.writerow((step,defined_offset,(total_matches/total_min_group),total_euclid_distance/number_of_groups))

    return total_matches, average_matches

#--------------------------------------------------
# reads in two files, sorts and then returns the two lists
def compare_files(file1,file2):
    print("Sorting inputs..")
    entries1 = [] # stores sorted contents of file in original format and sorts
    entries2 = [] # same for second file
    with open(file1, "r", errors="ignore") as f_my:
        try:
            for line in f_my:
                entries1.append(tuple(line.strip("\n").split(',')))
            entries1.sort(key=takeSecond)
        except Exception as e:
            print("error {} in line \'{}\', ignoring ".format(e, str(line)))
            print("Probably appears because of trailing newlines in file")
            pass

    with open(file2, "r", errors="ignore") as f_my:
        try:
            for line in f_my:
                entries2.append(tuple(line.strip("\n").split(',')))
            entries2.sort(key=takeSecond)
        except Exception as e:
            print("error {} in line \'{}\', ignoring ".format(e, str(line)))
            print("Probably appears because of trailing newlines in file")
            pass
    return entries1, entries2

try:
    assert (len(sys.argv) >= 3), "at least 2 file arguments required\n"
    file1 = str(sys.argv[1])
    file2 = str(sys.argv[2])
    try:
        RSSI_difference = int(sys.argv[3])
        RSSI_difference_enabled = True
    except:
        pass

# ===========================================================================
# ===========================================================================

except AssertionError as error:
    print("Invalid syntax: "+str(error))
    sys.exit(-1)

outfile = "time_comp_log_" + file1.split('.')[0] + "_" + file2.split('.')[0] + "_dff" + str(RSSI_difference)
with open(outfile, "w"): pass # clear contents of old file

entries1, entries2 = compare_files(file1,file2)

for step in range(5000,10000,5000):
    print("Computing step: {}".format(step))
    for offset in range(0,10000,5000):
        print("Computing offset: {}".format(offset))
        time_compare(entries1,entries2,step,offset)