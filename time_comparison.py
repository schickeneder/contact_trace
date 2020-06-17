import sys
# purpose of this program is to compare the capture logs grouped by user-defined time intervals and vary the offset
# to find the optimal synchronization based on visible APs rather than GPS, indicating a best case matching scenario

# currently uses the newer format..

pattern = '%Y-%m-%d %H:%M:%S'

def takeSecond(list):
    return int(list[1])

# return the longer time span of each of the file entries, based on the 2nd element (relative clock offset)
# note: if it seems too big, there may be some odd entries at the end of the file that may need to be removed
def get_longest_time_span(entries1,entries2):
    return max((int(entries1[-1][1])-int(entries1[0][1])), (int(entries2[-1][1])-int(entries2[0][1])))

# returns the number of matches for BSSID/MAC between groups (e.g. size of the intersect)
def count_BSSID_matches(group1, group2):
    group_intersect = []
    group1_BSSID = [item[3] for item in group1]
    group2_BSSID = [item[3] for item in group2]
    for BSSID in group1_BSSID:
        if BSSID in group2_BSSID:
            group_intersect.append(BSSID)
    return len(group_intersect)

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
                    entry not in group1:
                group1.append(entry)
        for entry in entries2:
            current_timestamp = int(entry[1])+offset
            if entry[0] == "WIFI" and current_timestamp < time_slice and current_timestamp > prev_slice and \
                    entry not in group2:
                group2.append(entry)

        # metrics.. but only count if two groups are present, e.g. a scan was performed during that time step
        if group1 and group2:
            current_matches = count_BSSID_matches(group1,group2)
            #print("Group1,Group2, matches: {},{},{}".format(len(group1),len(group2),current_matches))
            total_min_group += min(len(group1), len(group2))
            total_matches += current_matches
            total_group_discrepancy += abs(len(group1)-len(group2))
            number_of_groups += 1

        # get ready to start next group
        group1 = []
        group2 = []
        prev_slice = time_slice

    # report final numbers
    print("Summary---------------------------------------------")
    print("Step size: {} ms".format(step))
    print("Original offset, defined offset : {},{}".format((offset-defined_offset), defined_offset))
    print("Total Matches / Possible: {}/{}".format(total_matches,total_min_group))
    print("Average Match Percentage: {}".format(total_matches/total_min_group))
    print("Total Group Discrepancy / Number of Groups: {}/{}".format(total_group_discrepancy,number_of_groups))
    print("Average Group Discrepancy: {}".format(total_group_discrepancy/number_of_groups))

    return total_matches, average_matches

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
    assert (len(sys.argv) == 3), "2 file arguments required\n"
    file1 = str(sys.argv[1])
    file2 = str(sys.argv[2])

except AssertionError as error:
    print("Invalid syntax: "+str(error))
    sys.exit(-1)

entries1, entries2 = compare_files(file1,file2)
for step in range(1000,5000,1000):
    for offset in range(-2000,2000,500):
        time_compare(entries1,entries2,step,offset)