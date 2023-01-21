import os
import json


def parse_data(raw_data):
	raw_list = raw_data.split("||")
	data_list = []
	for item in raw_list: # item is a single observation: "time": 123343445, "data" : {...
		#print(item)
		#print("\n\n")
		try: # in case some weren't formatted correctly, skip a bad json.loads
			data_list.append(json.loads(item))
			#print(foo)
			#3for key in foo["data"]:
			#	print(foo["data"][key])
		except:
			pass
	return data_list

def import_data(filename):
	with open(filename,'r') as f:
		input = f.read()
	return input

def import_all_data(filepath):
	try:
		for file in os.listdir(filepath):
			filename = filepath + "/" + file
			print(import_data(filename))
	except:
		print("No files in {}".format(filepath))

def import_all_data_one_device(filepath,deviceID):
	found = False
	input = ""
	try:
		for file in os.listdir(filepath):
			if deviceID in file:
				found = True
				filename = filepath + "/" + file
				input += import_data(filename)
	except:
		print("No files in {}".format(filepath))
	if not found:
		print("No files for device ID {} found.".format(deviceID))
		return False
	else:
		return input

# create list of dictionaries where root is deviceID; each deviceID key contains all SSIDs; each SSID contains all RSSI
def BSSID_data_dict(data_list): # formatted like [{'time': 1673582493, 'data': {'14ebb620b2de': ['Redondo Rondo', -24, 4]
	BSSID_dict = {}
	for entry in data_list:
		for BSSID in entry["data"]:
			if BSSID not in BSSID_dict:
				BSSID_dict[BSSID] = {"SSID":entry["data"][BSSID][0],
									 "channel":entry["data"][BSSID][2],
									 "RSSI":[entry["data"][BSSID][1]]}
			BSSID_dict[BSSID]["RSSI"].append(entry["data"][BSSID][1]) # append the RSSI observation to the list
	return BSSID_dict

# returns list of deviceIDs based on filenames where filename is xxxxx_x_x_Xx_x_deviceID_#
def get_devIDs(filepath):
	deviceID_list = []
	try:
		for filename in os.listdir(filepath):
			deviceID = filename.split("_")[-2]
			if deviceID not in deviceID_list: # make it a unique list
				deviceID_list.append(deviceID)
	except:
		pass

	if deviceID_list:
		return deviceID_list

if __name__== "__main__":
	print("Running main")
	device_list = get_devIDs("data")
	for devID in device_list:
		raw_data = import_all_data_one_device("data",devID)
		data_list = parse_data(raw_data)
		BSSID_dict = BSSID_data_dict(data_list)
		print(BSSID_dict)
	#import_all_data("data")
	# data_list = store_data(import_data('data/12Jan2023_21_09_13_0ac8c400_1'))
	# print(data_list)
	# foo = BSSID_data_dict(data_list)
	# print(foo)