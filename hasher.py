import time, hashlib, os

pattern = '%Y-%m-%d %H:%M:%S'
group_span = 100 # seconds

#in_files = ['20200507_capture_axon7.csv','20200507_capture_pixel3a.csv','20200507_capture_trackphone.csv']
#out_files = ['hash1_axon7', 'hash2_pixel3a', 'hash3_track']
in_files = []
out_files = []

# generate appropriate file names if none provided
if not in_files:
    for filename in os.listdir():
        filename_parts = filename.split('.')
        if filename_parts[-1].lower() == "csv":
            print(filename)
            in_files.append(filename)
            out_files.append(filename_parts[0]+".hash")

key_group_counter = 0
current_group = []
# generate hash for each wifi line in input file, write to output file
for infile, outfile in zip(in_files,out_files):
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
                    print("-----------New Group-----------")
                    key_group_counter = epoch
                    current_group = []
                to_add = ready + ":" + hash
                if to_add not in current_group: # prevent redundant entries
                    current_group.append(ready + ":" + hash)
                    f_out.write(hash + "\n")
                #print(tmp[0].replace(':','').upper(),tmp[1],tmp[3])
                #print(epoch)
                #print(hash, end = '')
                #print(" " + ready)


