import random
import requests
from timeit import default_timer as timer
import json

num_bits = 32
num_keys = 10000 # ~144*7*10 or 144 groups (every 10 min), 10 per group, 7 days
url = "http://localhost:5000/check_contact"

#32 bits, 5000 keys, 300M in server ~ 0.034s
#32, 10000, 300M ~ 0.064s
#32, 500, 300M ~ 0.0057s
#32, 1M, 300M ~ 7.24s, 5.8s w/o printing
tests = []
for i in range(1,num_keys):
	tests.append(random.getrandbits(num_bits))


with open("client_keys_"+str(num_keys),"w") as f:
	f.write(str(tests))

start = timer()
x = requests.post(url, data = str(tests))
stop = timer()
count = 0
items = json.loads(x.text)
#print(items)
for item in items:
	if int(item):
		count = count + 1

print("Results {}/{} in {} seconds".format(count,len(items),stop-start))