import time, hashlib, os
#TODO: hash groups of APs at the same time for a given key
# hash of top 3 access points good enough?
# maybe order hashes in order of decreasing rss?
# how accurate are these as measures of distance between individuals? How to test?
# false positives = says you came in contact but actual distances are too far to be concerning
pattern = '%Y-%m-%d %H:%M:%S'
group_span = 5 # seconds

in_files = ['walk_dual_colocated_axon_converted.csv','walk_dual_colocated_pixel_converted.csv']
out_files = ['hash1_axon7.hash', 'hash2_pixel3a.hash']
#in_files = []
#out_files = []

# generate appropriate file names if none provided
if not in_files:
    for filename in os.listdir():
        filename_parts = filename.split('.')
        if filename_parts[-1].lower() == "csv":
            in_files.append(filename)
            out_files.append(filename_parts[0]+".hash")


# generate hash for each wifi line in input file, write to output file
for infile, outfile in zip(in_files,out_files):
    print("Processing {}".format(infile))
    key_group_counter = 0
    current_group = []
    group_key = 0
    with open(infile) as f, open(outfile,"w+") as f_out:
        for line in f:
            tmp = line.strip('\n').split(',')
            if tmp[-1] == 'WIFI':
                bssid = tmp[0].replace(':','').upper()
                ssid = tmp[1]
                epoch = int(time.mktime(time.strptime(tmp[3], pattern))) #epoch time in seconds
                ready = str(bssid) + str(ssid) + str(epoch//group_span)
                hash = hashlib.sha256(ready.encode()).hexdigest()
                if epoch > key_group_counter + group_span: # this group is done
                    print(current_group)
                    print("-----------Last Group: {} items until {}".format(len(current_group), epoch))
                    # print current group to a file
                    group_key = group_key // 2^64
                    for key in current_group:
                        try:
                            f_out.write(key.split(':')[-1] + ":" + hex(group_key).lstrip('0x')+'\n')
                        except:
                            print("Couldn't write to file")
                    key_group_counter = epoch
                    current_group = []
                    group_key = 0
                    print("-----------New Group-----------")
                to_add = ready + ":" + hash
                if to_add not in current_group: # prevent redundant entries
                    current_group.append(ready + ":" + hash)
                    group_key += int(hash,16)
                #print(tmp[0].replace(':','').upper(),tmp[1],tmp[3])
                #print(epoch)
                #print(hash, end = '')
                #print(" " + ready)


