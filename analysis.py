import os
import json


def store_data(raw_data):
	raw_list = raw_data.split("||")
	data_list = []
	for item in raw_list: # item is a single observation: "time": 123343445, "data" : {...
		#print(item)
		#print("\n\n")
		try: # in case some weren't formated correctly, skip a bad json.loads
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

if __name__== "__main__":
	print("Running main")
	#import_all_data("data")
	data_list = store_data(import_data('data/12Jan2023_21_09_13_0ac8c400_1'))
	print(data_list)
	foo = BSSID_data_dict(data_list)
	print(foo)