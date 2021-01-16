
import random
from flask import Flask, jsonify
app = Flask(__name__)

hashes = {}
num_bits = 16


@app.route('/')
def default():
	response = "Number of hashes is {}".format(len(hashes))
	return response

@app.route('/check_contact')#, methods=['POST'])
def return_matches():
	#response = "Number of hashes is {}".format(len(hashes))
	#this is just a temporary test
	tests = []
	for i in range(1,100):
		tests.append(random.getrandbits(num_bits))
	response = []
	for item in tests:
		try:
			print("Trying {}".format(item))
			response.append(hashes[item])
		except:
			pass
	return jsonify(response)

def main():

	num_hashes = 5000000
	for i in range(1,num_hashes):
		hashes[random.getrandbits(num_bits)] = 3 #random.randint(-90,-10)

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