import time, hashlib, os

pattern = '%Y-%m-%d %H:%M:%S'

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

# generate hash for each wifi line in input file, write to output file
for infile, outfile in zip(in_files,out_files):
    with open(infile) as f, open(outfile,"w+") as f_out:
        for line in f:
            tmp = line.strip('\n').split(',')
            if tmp[-1] == 'WIFI':
                bssid = tmp[0].replace(':','').upper()
                ssid = tmp[1]
                epoch = int(time.mktime(time.strptime(tmp[3], pattern)))
                #print(tmp[0].replace(':','').upper(),tmp[1],tmp[3])
                #print(epoch)
                ready = str(bssid) + str(ssid) + str(epoch//100)
                print(ready)
                hash = hashlib.sha256(ready.encode()).hexdigest()
                print(hash)
                f_out.write(hash+"\n")


