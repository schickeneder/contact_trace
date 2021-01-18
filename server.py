
import random
from flask import Flask, jsonify, request, json
app = Flask(__name__)

hashes = {}
num_bits = 32
population_size = 1000000
reported_carriers = 0.1*population_size
num_hashes = int(100000)

#30, 100M ~ 17.6 (15) GB total
#30, 120M ~ 18.8 (16)
#32, 100M ~ 18.3 (16) 
#32, 150M ~ 20.1 (18)
#32, 190M ~ 25.4 (23)
#32, 200M ~ 25.4 (23)
#32, 220M ~ 26   (24)
#32, 240M ~ 26.6
#32, 300M ~ 28.3


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

@app.route('/check_contact', methods=['POST'])
def return_matches():
	#response = "Number of hashes is {}".format(len(hashes))
	#this is just a temporary test
	keylist = json.loads(request.data)
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

def main():

	for i in range(1,num_hashes):
		hashes[random.getrandbits(num_bits)] = 3 #random.randint(-90,-10)
	print("Generated {} hashes".format(len(hashes)))

	# may not alway print the correct number because there were some redundant hashes..
	#print(len(hashes))

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
    main()
main()