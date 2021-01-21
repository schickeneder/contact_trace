import random
import requests
import sys
from timeit import default_timer as timer
from hashlib import sha1
from flask import Flask, jsonify, request
app = Flask(__name__)

hashes = {}
num_bits = 48 # overwritten by commandline arguments
num_hashes = int(10000000) # overwritten by commandline arguments

#30, 100M ~ 17.6 (15) GB total
#30, 120M ~ 18.8 (16)
#32, 100M ~ 18.3 (16) 
#32, 150M ~ 20.1 (18) [9.6 GB]
#32, 190M ~ 25.4 (23)
#32, 200M ~ 25.4 (23)
#32, 220M ~ 26   (24)
#32, 240M ~ 26.6
#32, 300M ~ 28.3      [19.1GB]

#with gunicorn gevent, 1 worker
#48, 300M 19.1GB ~28s for 1000*1000
#48, 350M 20.6GB ~27s

@app.route('/')
def default():
	response = "Number of hashes is {}".format(len(hashes))
	return response

@app.route('/sim_check_contact')#, methods=['POST'])
def sim_return_matches():
	#response = "Number of hashes is {}".format(len(hashes))
	#this is just a temporary test
	tests = []
	for i in range(1,100):
		tests.append(random.getrandbits(num_bits))
	response = []
	for item in tests:
		try:
			#print("Trying {}".format(item))
			response.append(hashes[item])
		except:
			pass
	return jsonify(response)

#https://stackoverflow.com/questions/10434599/get-the-data-received-in-a-flask-request
@app.route('/check_contact', methods=['POST'])
def return_matches():
	#response = "Number of hashes is {}".format(len(hashes))
	#this is just a temporary test
	keylist = request.get_json()
	#print("Request received: {}".format(keylist))
	response = []

	for key in keylist:
		try:
			#print("Trying {}".format(key))
			response.append(hashes[int(key)])
		except:
			response.append(0)
			pass
	return jsonify(response)


@app.route('/auth_check_contact/<token>/<secret>', methods=['POST'])
def auth_return_matches(token = 0, secret=0):

	if (secret != sha1(token.encode()).hexdigest()):
		return "Bad Authentication" 

	keylist = request.get_json()
	response = []

	for key in keylist:
		try:
			#print("Trying {}".format(key))
			response.append(hashes[int(key)])
		except:
			response.append(0)
			pass
	return jsonify(response)

#this approach is too slow, instead have the user contact the key_auth to obtain token
#then present the token to the server
@app.route('/old_auth_check_contact/<token>', methods=['POST'])
def old_auth_return_matches(token = 0):

	if not (auth_token(token)):
		print("Bad token")
		return "Bad token"

	keylist = request.get_json()
	response = []

	for key in keylist:
		try:
			#print("Trying {}".format(key))
			response.append(hashes[int(key)])
		except:
			response.append(0)
			pass
	return jsonify(response)

def random_generate_hashes(number_of_hashes):
	start = timer()
	for i in range(0,number_of_hashes):
		hashes[random.getrandbits(num_bits)] = int(2e9)
	print("Generated {}, {}-bit \"hashes\" in {} seconds.".format(len(hashes), num_bits, timer()-start))

def setup(arg1,arg2):
	global num_bits
	global num_hashes
	num_bits = int(arg1)
	num_hashes = int(arg2)
	random_generate_hashes(num_hashes)
    # try:
    #     assert (len(sys.argv) >= 2), "at least 1 argument required\n"
    #     num_hashes = str(sys.argv[1])
    #     try:
    #         file2 = str(sys.argv[2])
    #     except:
    #         file2 = 0
    #         pass

    # except AssertionError as error:
    #     print("Invalid syntax: " + str(error))
    #     sys.exit(-1)
if __name__ == '__main__':
    setup(sys.argv[1],sys.argv[2])
    app.run(host='0.0.0.0',port=5000, use_reloader=False)

