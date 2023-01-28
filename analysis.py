import os
import json
from statistics import variance, mean
import matplotlib.pyplot as plt
from numpy.random import randint


# this is used to analyze wifi scan logs collected from https://github.com/schickeneder/WiFi_Scanner_micropython
# this is not used for wiglnet wifi dumps collected from phones
# TODO: this would be a cleaner implementation as a class..


class rxnode:

    master_AP_list = {"BSSID_list": [], "SSID_list": [], "channel_list": []} # store BSSID, SSID, channel for all devID
    def __init__(self,devID):
        self.devID = devID # unique device ID which is usually a MAC address like "1a2dc9d20a"
        self.data = {} # contains all observations like:
        # "<BSSID1>" : {"SSID" : "<SSID1>", "channel": 2, "RSSI_list": [-20,-34], "timestamps": [12461,12463]}
        # may need to adjust this because channel could change..
        self.min_time = 0 # once data is assigned, stores the earliest timestamp
        self.max_time = 0 # " " latest timestamp
        self.AP_list = {"BSSID_list": [], "SSID_list": [], "channel_list": []} # instance AP list, common index

    # should call after importing data
    def update_master_AP_list(self):
        try:
            for BSSID,SSID,channel in zip(self.AP_list["BSSID_list"],
                                          self.AP_list["SSID_list"],self.AP_list["channel_list"]):
                if BSSID not in self.master_AP_list["BSSID_list"]:
                    rxnode.master_AP_list["BSSID_list"].append(BSSID)
                    rxnode.master_AP_list["SSID_list"].append(SSID)
                    rxnode.master_AP_list["channel_list"].append(channel)
        except:
            "ERROR: Couldn't append AP list info for devID {} to master_AP_list".format(self.devID)

    def get_AP_list(self):
        return self.AP_list

    def get_master_AP_list(self):
        return self.master_AP_list

    # imports data for this devID from filepath
    # protocol version describes which file format to use for import, default is "0" which is what we used for nodeMCUs
    def import_data(self,filepath="data", protocol_version="0"):

        # import data to data_list
        if not protocol_version == "0":
            print("ERROR:Protocol version {} not supported".format(protocol_version))
            return
        raw_data = import_all_data_one_device(filepath, self.devID)
        data_list = parse_data(raw_data) # looks like [{"time": 1674503222, "data": {"1aebb620b2de": ["MAGA", -63, 4]}},

        # load data into rxnode instance
        for entry in data_list:
            for BSSID in entry["data"]:
                if BSSID not in self.data: # create new entry
                    self.data[BSSID] = {"SSID": entry["data"][BSSID][0],"channel": entry["data"][BSSID][2],
                                         "RSSI_list": [],"timestamps": []}
                self.data[BSSID]["RSSI_list"].append(entry["data"][BSSID][1])
                self.data[BSSID]["timestamps"].append(entry["time"])

        self.AP_list["BSSID_list"], self.AP_list["SSID_list"], self.AP_list["channel_list"] = get_APs(data_list)
        self.update_master_AP_list()

# parses any amount of raw_data that has been imported from files
# raw_data looks like: {"time": 1674503222, "data": {"1aebb620b2de": ["MAGA", -63, 4]}}||{"time": 1674503222,..
# where each observation denoted by a unix timestamp time is separated by '||' to easily delimit
# returns a data_list consisting of a list of dictionaries in the same format
def parse_data(raw_data):
    raw_list = raw_data.split("||")
    data_list = []
    for item in raw_list:  # item is a single observation: "time": 123343445, "data" : {...
        # print(item)
        # print("\n\n")
        try:  # in case some weren't formatted correctly, skip a bad json.loads
            data_list.append(json.loads(item))
        except:
            pass
    return data_list


def import_data(filename):
    with open(filename, 'r') as f:
        input = f.read()
    return input


# incomplete and not currently used
def import_all_data(filepath):
    try:
        for file in os.listdir(filepath):
            filename = filepath + "/" + file
            print(import_data(filename))
    except:
        print("No files in {}".format(filepath))


# imports contents of all files with deviceID in the name,
# concatenates data into "raw_data" format for use with parse_data()
def import_all_data_one_device(filepath, deviceID):
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


def import_all_data_all_devices(filepath, device_list):
    input = ""
    for devID in device_list:
        input += import_all_data_one_device(filepath, devID)

    return input


# create list of dictionaries where root is deviceID; each deviceID key contains all SSIDs;
# each SSID contains all RSSI
def BSSID_data_dict(
        data_list):  # formatted like [{'time': 1673582493, 'data': {'14ebb620b2de': ['Redondo Rondo', -24, 4]
    BSSID_dict = {}
    for entry in data_list:
        for BSSID in entry["data"]:
            if BSSID not in BSSID_dict:
                BSSID_dict[BSSID] = {"SSID": entry["data"][BSSID][0],
                                     "channel": entry["data"][BSSID][2],
                                     "RSSI": [entry["data"][BSSID][1]]}
            BSSID_dict[BSSID]["RSSI"].append(entry["data"][BSSID][1])  # append the RSSI observation to the list
    return BSSID_dict


# returns list of deviceIDs based on filenames where filename is xxxxx_x_x_Xx_x_deviceID_#
def get_devIDs(filepath):
    deviceID_list = []
    try:
        for filename in os.listdir(filepath):
            deviceID = filename.split("_")[-2]
            if deviceID not in deviceID_list:  # make it a unique list
                deviceID_list.append(deviceID)
    except:
        pass

    if deviceID_list:
        return deviceID_list


def print_variance(device_list):
    for devID in device_list:
        raw_data = import_all_data_one_device("data", devID)
        data_list = parse_data(raw_data)
        BSSID_dict = BSSID_data_dict(data_list)
        print("devID,{}".format(devID))
        for BSSID in BSSID_dict:
            print("BSSID,{},SSID,{},channel,{},RSSI,mean/var,{},{}".format(BSSID, BSSID_dict[BSSID]["SSID"],
                                                                           BSSID_dict[BSSID]["channel"],
                                                                           mean(BSSID_dict[BSSID]["RSSI"]),
                                                                           variance(BSSID_dict[BSSID]["RSSI"])))


# inputs a device list and returns unique lists of associated BSSID, SSID, channel
# data_list entry looks like: {'time': 1673620424, 'data': {'14ebb620b2de': ['Redondo Rondo', -25, 4], '1eebb620b2de':
def get_APs(data_list):
    BSSID_list = []
    SSID_list = []
    channel_list = []
    for entry in data_list:
        for BSSID in entry["data"]:
            if BSSID not in BSSID_list:
                BSSID_list.append(BSSID)
                SSID_list.append(entry["data"][BSSID][0])
                channel_list.append(entry["data"][BSSID][2])
    return BSSID_list, SSID_list, channel_list


def print_CSV_RSSI(device_list):
    BSSID_list = []
    for devID in device_list:
        raw_data = import_all_data_one_device("data", devID)
        data_list = parse_data(raw_data)
        # for item in data_list:
        #	print(item)
        BSSID_list, SSID_list, channel_list = get_APs(data_list)
        for BSSID, SSID, channel in zip(BSSID_list, SSID_list, channel_list):
            print("{}_{}_{}".format(BSSID, SSID, channel), end=",")
        for entry in data_list:
            print("{}".format(entry["time"]), end=",")
            for BSSID in BSSID_list:
                if BSSID in entry["data"]:
                    print(entry["data"][BSSID][1], end=",")
                else:
                    print("", end=",")
            print("")


def write_CSV_RSSI(device_list):
    BSSID_list = []
    for devID in device_list:
        raw_data = import_all_data_one_device("data", devID)
        data_list = parse_data(raw_data)

        filename = devID + "_timestamped_RSSI.csv"
        with open(filename, "w") as f:
            BSSID_list, SSID_list, channel_list = get_APs(data_list)
            f.write("Timestamp,")
            for BSSID, SSID, channel in zip(BSSID_list, SSID_list, channel_list):
                f.write("{}_{}_{},".format(BSSID, SSID, channel))
            f.write("\n")
            for entry in data_list:
                f.write("{},".format(entry["time"]))
                for BSSID in BSSID_list:
                    if BSSID in entry["data"]:
                        f.write("{},".format(entry["data"][BSSID][1]))
                    else:
                        f.write(",")
                f.write("\n")


# plots all RSSI measurements for each BSSID in one figure for the given deviceID
def plot_device_all_APs(deviceID):
    RSSI_dict = {}
    raw_data = import_all_data_one_device("data", deviceID)
    data_list = parse_data(raw_data)

    BSSID_list, SSID_list, channel_list = get_APs(data_list)
    # entry looks like: {'time': 1673620424, 'data': {'14ebb620b2de': ['Redondo Rondo', -25, 4], '1eebb620b2de': ['Foo..
    for entry in data_list:
        for BSSID in BSSID_list:  # check for each BSSID (AP)
            if BSSID in entry["data"]:
                if BSSID not in RSSI_dict:  # create the entry
                    RSSI_dict[BSSID] = {}
                    RSSI_dict[BSSID]["time"] = []
                    RSSI_dict[BSSID]["RSSI"] = []
                timestamp = entry["time"]
                if timestamp > 10000:  # needs to be unix time, and not 0
                    RSSI_dict[BSSID]["time"].append(timestamp)  # append this timestamp to the list
                    RSSI_dict[BSSID]["RSSI"].append(entry["data"][BSSID][1])  # append RSSI to list
    # return RSSI_dict

    fig, ax = plt.subplots()

    # c = randint(1,10,size=len(RSSI_dict))

    scatters = []
    for BSSID in RSSI_dict:
        # fig = plt.figure()
        print(RSSI_dict[BSSID])  # ["time"],RSSI_dict[BSSID]["RSSI"])
        SSID = SSID_list[BSSID_list.index(BSSID)]
        scatter = ax.scatter(RSSI_dict[BSSID]["time"], RSSI_dict[BSSID]["RSSI"], label=BSSID + " " + SSID, marker=".")
        scatters.append(scatter)

    plt.title("Device: {}".format(deviceID))
    ax.legend(handles=scatters, loc="lower left", title="BSSIDs")
    plt.show()
    print(SSID_list)


def get_RSSI_dict(BSSID):
    device_list = get_devIDs("data")
    RSSI_dict = {}  # looks like {"deviceid1" : {"time" : [123003, 123004..], "RSSI" : [-24,-67,..]} , "devid2"..

    for deviceID in device_list:
        raw_data = import_all_data_one_device("data", deviceID)
        data_list = parse_data(raw_data)

        # entry looks like: {'time': 1673620424, 'data': {'14ebb620b2de': ['Redondo Rondo', -25, 4], '1eebb620b2de': ['Foo..
        for entry in data_list:
            if BSSID in entry["data"]:
                if deviceID not in RSSI_dict:  # create the entry
                    RSSI_dict[deviceID] = {}
                    RSSI_dict[deviceID]["time"] = []
                    RSSI_dict[deviceID]["RSSI"] = []
                if entry["time"] > 10000:  # make sure it has a real time
                    RSSI_dict[deviceID]["time"].append(entry["time"])  # append this timestamp to the list
                    RSSI_dict[deviceID]["RSSI"].append(entry["data"][BSSID][1])  # append RSSI to list

    BSSID_list, SSID_list, channel_list = get_APs(data_list)
    if BSSID in BSSID_list:
        SSID = SSID_list[BSSID_list.index(BSSID)]
    else:
        SSID = "unknown"

    return RSSI_dict, SSID


# plots all RSSI measurements for each deviceID in one figure for the given BSSID
# skip if time = 0, means it hasn't synced clock
def plot_all_APs(RSSI_dict, SSID):
    fig = plt.figure()

    for deviceID in RSSI_dict:
        # print(RSSI_dict[deviceID])
        plt.scatter(RSSI_dict[deviceID]["time"], RSSI_dict[deviceID]["RSSI"], marker=".")

    plt.title("BSSID: {} - {}".format(BSSID, SSID))
    #plt.ion()
    plt.show()
    plt.pause(0.001)
    print(BSSID_list)


# returns corrected variance over selected intervals with the average of each interval shifted to 0
# inputs timestamps and RSSI and sampling interval
# can be input of just one BSSID, to include multiple at once, would need to offset timestamps
# if otherwise overlapping, to keep them separate
# normalizes average over each interval by shifting to 0, to achieve consistent variance across samples
# interval should be in seconds; relevant intervals for contact tracing are 1 min, 10 min, 30 min
# interval 0 returns variance of whole set.
def get_variance(timestamps, RSSI, interval=0):
    if not timestamps:
        return -2
    corrected_RSSI = []
    min_timestamp = min(timestamps)
    if interval == 0 and len(RSSI) > 1:
        return variance(RSSI)
    last_timestamp = 0
    next_interval = timestamps[0] + interval
    tmp_RSSI = []
    for timestamp, RSS in zip(timestamps, RSSI):
        if timestamp < last_timestamp:
            print("Timestamps out of order!!")
            return -2
        else:
            last_timestamp = timestamp

        if timestamp > next_interval:  # package up this interval
            if tmp_RSSI:
                tmp_mean = mean(tmp_RSSI)
                corrected_RSSI += [x - tmp_mean for x in tmp_RSSI]
            tmp_RSSI = []
            next_interval += interval
        else:  # keep adding for the current interval
            tmp_RSSI.append(RSS)

    # print(corrected_RSSI)
    if len(corrected_RSSI) > 1:
        return variance(corrected_RSSI)
    else:
        return -1


def print_all_var(BSSID_list):
    for BSSID in BSSID_list:
        RSSI_dict, SSID = get_RSSI_dict(BSSID)
        print("BSSID|SSID : {}|{}".format(BSSID, SSID))
        for devID in RSSI_dict:
            cvar = get_variance(RSSI_dict[devID]["time"], RSSI_dict[devID]["RSSI"], 60)
            if len(RSSI_dict[devID]["RSSI"]) > 1:
                var = variance(RSSI_dict[devID]["RSSI"])
                meanRSS = mean(RSSI_dict[devID]["RSSI"])
            else:
                var = -1
            if var > 1:  # sometimes will be var but no cvar due to the intervals
                print("Mean/Var/C-Var for {} is {:.2f}/{:.2f}/{:.2f}".format(
                    devID, meanRSS, var, cvar))

# for each time <interval> in RSSI data, compares RSSIs across of all APs across two devices and plots number of matches
# a match occurs if RSSIs for the same AP/BSSID are within <threshold>
# if more than one RSSI are recorded for the same BSSID in an interval, the higher RSSI is used
# the color of each devID is consistent across intervals
def match_all_APs(RSSI_dict, threshold, interval=60):
    for devID in RSSI_dict:
        intervals = [] # stores the timestamp of each interval, i.e. a decimation of dev_timestamps
        matches = [] # stores the number of matches in each interval
        dev_timestamps = RSSI_dict[devID]["time"]
        dev_RSSI = RSSI_dict[devID]["RSSI"]
        current_interval = dev_timestamps[0] # start at the beginning
        for devID2 in RSSI_dict: # compare against each other device
            if devID == devID2:
                continue # we don't need to compare against itself..
            dev2_timestamps = RSSI_dict[devID2]["time"]
            dev2_RSSI = RSSI_dict[devID2]["RSSI"]
        # TODO maybe find a better way to do this with numpy? as vectors rather than loops?
        last_timestamp = 0
        next_interval = timestamps[0] + interval
        tmp_RSSI = []
        for timestamp, RSS in zip(timestamps, RSSI):
            if timestamp < last_timestamp:
                print("Timestamps out of order!!")
                return -2
            else:
                last_timestamp = timestamp

            if timestamp > next_interval:  # package up this interval
                if tmp_RSSI:
                    tmp_mean = mean(tmp_RSSI)
                    corrected_RSSI += [x - tmp_mean for x in tmp_RSSI]
                tmp_RSSI = []
                next_interval += interval


# def write_timestamped_RSSI(device_list):
# 	for devID in device_list:
# 		raw_data = import_all_data_one_device("data",devID)
# 		data_list = parse_data(raw_data)
# 		BSSID_dict = BSSID_data_dict(data_list)
# 		print("devID,{}".format(devID))
# 		for BSSID in BSSID_dict:
# 			print("BSSID,{},SSID,{},channel,{},RSSI,mean/var,{},{}".format(BSSID,BSSID_dict[BSSID]["SSID"],
# 																		   BSSID_dict[BSSID]["channel"],
# 				  mean(BSSID_dict[BSSID]["RSSI"]),
# 				  variance(BSSID_dict[BSSID]["RSSI"])))

if __name__ == "__main__":
    print("Running main")
    # Jan12 data
    # BSSID_list = ['14ebb620b2de', '1eebb620b2de', '1aebb620b2de', '66a6e6eef45e', '3e6105d41631',
    # 			  '5ca6e6eef45e', '08b4b143c94d', '62a6e6eef45e', '0c83ccf9ff11', '28bd897c636d', '8e4962ecf8e6']
    # Jan23 data
    # BSSID_list = ['1eebb620b2de', '1aebb620b2de', '5ca6e6eef45e', '08b4b143c94d', '08b4b18135b7', '14ebb620b2de',
    # 			  '54833aa79b17', '0c83ccf9ff11', '4ca64d80cb60', '4ca64d80cb62', '62a6e6eef45e', '66a6e6eef45e',
    # 			  '4ca64d80cb64', '1262e5fe0957', '8e4962ecf8e6', 'd6351da76bcd', '08b4b14baa20', '28bd897c62e9',
    # 			  'd6351d56bb20', '28bd897c636d', '08b4b143fc4e', '4ca64d80cb61', '4ca64d80cb63', '54833a7fc55f',
    # 			  '10e7c6c68147', '22ad5625c86f', '4ca64d7f9081', '28bd897d4335', 'a638f0a5395f', '4ca64d7f9084',
    # 			  '4ca64d7f9083', '28bd897c01cd', '4ca64d7f9080', '60b76ef711d9', '08b4b18132aa', 'bc825d68bd64',
    # 			  'ba9f0965e4c0', 'fa8fca8526ef', '8a5a85e5181d', '087190464259', 'bc825db69f49', '32b4b8ebda2b',
    # 			  'bc825d67d1c5', '0054af64b201', '22ad562a1d31', '4ca64d7f9082', 'c449bb904098', '886ae38017ac',
    # 			  'd040efc4dffa', '0054afe8bc76', '0054af850c1e', '2cdcad538a92', '94b86d4c5e8c', 'e046e512960e',
    # 			  'f855cdea9261', '7274144c06e5', 'bc825d688363', '9a4914a6faa0', 'f855cddb9511', '0054afcbb6cc',
    # 			  '629944963687', '9a49149c090a', 'b00594263ea1', 'b200733ed4f2', '62e6f09a243e', '78617c1896d6',
    # 			  '8a5a855abe3f', '006ff2304178', 'c449bbca1c0a', 'bc825d9dd528', 'bc825d8a36c5', '12e8a7b3be72',
    # 			  '8a5a85c58d3a', 'c449bb9f98dc', '46916049de42', 'c449bb4f34c2', '22ad563b9d5d', 'ac5d5ce7bd9e',
    # 			  '00a0dee1a437', '2880a239b29d', '40bd327740b5', '22ad5630af34', '62e6f09a9f86', '22ad5629602a',
    # 			  'cec0798cc96c', '780473e94c6e', '0254aff4dac9', '8a5a85e36da3', 'b20073d3b8fc', '0054af335609',
    # 			  'f855cdee9172', 'a2c9a09e1d40', '62e6f0635625', 'd040ef8974bf', '8a5a85ad408f', '22ad5647633a',
    # 			  'f0ab54a6d370', 'b200734fe0bc', '0054afd09dc2', '0254afd0decd', 'f855cd67af4b', '0054af6a40c5',
    # 			  'f0fe6bf4910c', 'bc428cf1973c', 'bc825dcffd8b', 'c449bb2a7d2c', '9e50d1f6830c', 'd626a4ddb461',
    # 			  '583277e9069c', 'c449bbf71eac', '5a6a0a2f2f40', '000af5691954', '62e6f019971d', '0254aff954ee',
    # 			  'e046e512b972', 'b200737201b4', '40bd327e9901', '0026b41d7f0a', '2880a2fed84e', '9a4914a6ccc8',
    # 			  'f855cdeb116c', 'bc825d2bd774', '62e6f0bb77b7', 'bc825d0e1d00', '26cd8d10bdad', '0017cad51fc6',
    # 			  '22ad562f53d5', '001cd72ff109']

    # Jan13 data
    # BSSID_list = ['1aebb620b2de', '1eebb620b2de', '0c83ccf9ff11', '66a6e6eef45e', '14ebb620b2de', '08b4b143c94d',
    #               '5ca6e6eef45e', '62a6e6eef45e', '28bd897c636d', '08b4b14baa20', '54833a7fc55f', '8e4962ecf8e6',
    #               '08b4b18135b7', '28bd897c62e9', 'c449bbf6fe9a', 'd6351da76bcd', '08b4b18132aa', 'd6351d56bb20',
    #               'b00594263ea1', '100c6b115ac1', '160c6b115ac1', 'c6a5119ac5b1', 'c2a5119ac5b1', '1262e5fe0957',
    #               'fa8fca8526ef', '30e1714ee5ce', '886ae38017ac', '10e7c6c68147', '58cb52bf78e8', '4ca64d80cb61',
    #               '4ca64d7f9084', '28bd897c01cd', '4ca64d7f9081', '4ca64d7f9080', '4ca64d7f9083', '4ca64d7f9082',
    #               '4ca64d805f61', '4ca64d805f63', '28bd897d4335', '4ca64d80cb63', '4ca64d805f60', '4ca64d805f62',
    #               '4ca64d805f64', '4ca64d80acc1', '60b76ef711d9', '4ca64d80cb60', '08b4b1dd1b26', '54833a954e3f',
    #               '4ca64d80cb62', '4ca64d80cb64', '4ca64d80acc0', '4ca64d80acc2', '4ca64d80acc3', '22ad562727b4',
    #               '0c75bdd3bf80', '0c75bdd3bf82', 'f0fe6bf4910c', '4ca64d80acc4', 'ba9f09193d1d', '5c969d689707',
    #               '08b4b143fc4e', '723acb016f74', '703acb016f74', 'b06a41c0020e', '0054af6d37ff', '62e6f0b4de6b',
    #               '026ae38ab027', '54833aa79b17', '0c75bdd3bf81', '0c75bdd3bf84', '0c75bdd3bf83', '1e59c03c3825',
    #               '1a59c03c3825', '0054afa883b7', '0254affe0341', '0026b49e2b28', '0254aff4228c', '8c85805c3820',
    #               '00226cf0274c', 'ce6079796681', '12e8a782981c', '32b4b82791b5', '0054afc8746f', '7cfc3cb62af4']
    # device_list = ['3c6105d37067', 'e8db84c4c80a', 'e8db84c62200', '3c6105d41631', 'e8db84c620b1', '3c6105d37f73',
    #                'e8db84c4c0b0', '3c6105d49ef8', '3c6105d3a726']


    device_list = get_devIDs("data")
    print(device_list)

    node1 = rxnode('3c6105d37067')
    node1.import_data()
    print("node AP list is {}".format(node1.get_AP_list()))
    print("master AP list is {}".format(node1.get_master_AP_list()))

    BSSID_list, SSID_list, channel_list = get_APs(parse_data(import_all_data_all_devices("data", device_list)))
    print("BSSID list: {}".format(BSSID_list))
    print("SSID list: {}".format(SSID_list))
    print("channel list: {}".format(channel_list))

    # write_CSV_RSSI(device_list)

    # for devID in device_list:
    # 	plot_device_all_APs(devID)

	# print all variance and corrected variance
    #print_all_var(BSSID_list)

# for BSSID in BSSID_list:
# 	RSSI_dict, SSID = get_RSSI_dict(BSSID)
# 	print("BSSID|SSID : {}|{}".format(BSSID,SSID))
# 	plot_all_APs(RSSI_dict, SSID)

# for BSSID in BSSID_list:
# 	RSSI_dict, SSID = get_RSSI_dict(BSSID)
# 	print("BSSID|SSID : {}|{}".format(BSSID,SSID))
# 	for devID in RSSI_dict:
# 		cvar = get_variance(RSSI_dict[devID]["time"],RSSI_dict[devID]["RSSI"],60)
# 		if len(RSSI_dict[devID]["RSSI"]) > 1:
# 			var = variance(RSSI_dict[devID]["RSSI"])
# 			meanRSS = mean(RSSI_dict[devID]["RSSI"])
# 		else:
# 			var = -1
# 		if var > 1: # sometimes will be var but no cvar due to the intervals
# 			print("Mean/Var/C-Var for {} is {:.2f}/{:.2f}/{:.2f}".format(
# 				devID,meanRSS,var,cvar))
# plot_all_APs(RSSI_dict, SSID)

# print_var(device_list)
# print(BSSID_dict)
# import_all_data("data")
# data_list = store_data(import_data('data/12Jan2023_21_09_13_0ac8c400_1'))
# print(data_list)
# foo = BSSID_data_dict(data_list)
# print(foo)
