import random
import requests
from timeit import default_timer as timer
import json
import sys

num_bits = 48
num_keys = 1000 # ~144*7*10 or 144 groups (every 10 min), 10 per group, 7 days
address = "localhost:5000"
auth_token = "141497543794/493c74beaa272a2a1267678b97c439eaed919912"

def setup(arg1,arg2,arg3):
	global address
	global num_bits
	global num_keys
	address = str(arg1)
	num_bits = int(arg2)
	num_keys = int(arg3)

#32 bits, 5000 keys, 300M in server ~ 0.034s
#32, 10000, 300M ~ 0.064s
#32, 500, 300M ~ 0.0057s
#32, 1M, 300M ~ 7.24s, 5.8s w/o printing

def main():
	url = "http://" + address + "/check_contact"
	url_auth = "http://" + address + "/auth_check_contact/"
	#print("arg1, arg2, arg3: {}, {}, {}".format(address,num_bits,num_keys))
	tests = []
	for i in range(1,num_keys):
		tests.append(random.getrandbits(num_bits))

	keys = {'keylist':tests}

	with open("client_keys_"+str(num_keys),"w") as f:
		f.write(str(tests))

	start1 = timer()

	for count in range(1,1000):
		start2 = timer()
		#x = requests.post(url, json = tests)
		x = requests.post(url_auth + auth_token,
		 json = tests)

		stop2 = timer()

		count = 0
		items = json.loads(x.text)
		for item in items:
			if int(item):
				count = count + 1

		print("Results {}/{} in {} seconds".format(count,len(items),stop2-start2))
	stop1 = timer()
	print("Total elapsed time is {}".format(stop1-start1))



if __name__ == '__main__':
    setup(sys.argv[1],sys.argv[2],sys.argv[3])
    main()
