import sys

def findMatches(key_list,test_file):
    print("Looking for a match in this group {}".format(key_list))
    with open(test_file, "r") as f_test:
        test_current_group_key = ''
        test_group_count = 0
        test_group_matches = 0
        #TODO: need to keep track of how many matches per group
        for line in f_test:
            current_line_keys = line.strip('\n').split(':')
            if current_line_keys[1] != test_current_group_key: # new group
                if test_group_count > 0:
                    print("")
                test_group_count = 0
                test_current_group_key = current_line_keys[1] # set current group key
            else:
                test_group_count += 1

            if current_line_keys[0] in key_list:
                print(line)

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



