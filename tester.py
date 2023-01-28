import sys

# todo: also should write script to sync location with time for two entries to see how many *should* match

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

try:
    assert (len(sys.argv) == 3), "2 file arguments required\n"
except AssertionError as error:
    print("Invalid syntax: "+str(error))
    sys.exit(-1)

print(sys.argv)
my_file = str(sys.argv[1])
test_file = str(sys.argv[2])

with open(my_file,"r") as f_my:
    print("Opening files {} and {}".format(my_file,test_file))
    prev_group_key = ''
    my_current_group = []
    for line in f_my:
        current_line_keys = line.strip('\n').split(':')
        if current_line_keys[1] != prev_group_key:
            if(my_current_group):
                findMatches(my_current_group, test_file)
            prev_group_key = current_line_keys[1] # time to start building the next group
            my_current_group = []
        else:
            my_current_group.append(current_line_keys[0])



