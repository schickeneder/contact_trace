from analysis import *
import pickle

# This is a helper file to produce the match % vs RSSI threshold graphs

threshold = 53
interval = 10
#data_path = "data_Jan13_difrms"
# device list: ['3c6105d37067', 'e8db84c4c80a', 'e8db84c62200', '3c6105d41631', 'e8db84c620b1',
# '3c6105d37f73', 'e8db84c4c0b0', '3c6105d49ef8', '3c6105d3a726']
#data_path = "data_Feb09_difrms"
#data_path = "data_Jan12"
#data_path = "data_Jan23_all"
#data_path = "26Jan_testing - phones"


def get_nodes(device_list=None):
    if not device_list:
        device_list = get_devIDs(data_path)
    if not device_list:
        print("ERROR could not obtain device_list")
        return -1

    nodes = []
    for devID in device_list:
        node = rxnode(devID)
        node.import_data(data_path)
        nodes.append(node)

    return nodes


def get_matches_2_nodes(devID1,devID2,nodes):
    #global threshold
    #global interval
    for node1 in nodes:
        if node1.get_deviceID() == devID1:
            for node2 in nodes:
                if node2.get_deviceID() == devID2:
                    #print("Trying to match {} and {}".format(node1.get_deviceID(),node2.get_deviceID()))
                    matches,intervals,totals = match_all_APs3(node1,node2,threshold,interval)
                    #print("totals: {}/{}".format(sum(matches),sum(totals)))
                    return matches,intervals,totals


# device list: ['737fd300', '6770d300', '3116d400', '0022c600', '0ac8c400', 'b120c600', 'b0c0c400', '26a7d300']
def plot_matches_2_nodes(devID1,devID2, nodes):
    fig,ax = plt.subplots()
    matches,intervals,_ = get_matches_2_nodes(devID1,devID2,nodes)
    plot_matches(matches,intervals,"",ax)
    plt.title("Matches between {} and {}".format(devID1,devID2))
    fig.show()

#self.data = {}  # contains all measurements organized like:
# "<BSSID1>" : {"SSID" : "<SSID1>", "channel": 2, "RSSI_list": [-20,-34], "timestamps": [12461,12463]}
def plot_all_APs_node(node):
    fig, ax = plt.subplots()
    scatters = []
    data = node.get_data()
    for BSSID in data.keys():
        SSID = data[BSSID]["SSID"]
        scatter = ax.scatter(data[BSSID]["timestamps"], data[BSSID]["RSSI_list"], label=BSSID + " " + SSID, marker=".")
        scatters.append(scatter)

    plt.title("Device: {}".format(node.get_deviceID()))
    ax.legend(handles=scatters, loc="lower left", title="BSSIDs")
    plt.show()


def threshold_pair_comparison(nodelist1,nodelist2,nodes):
    global threshold
    threshold_list = []
    match_list = []
    totals_list = []

    for threshold in range(1,51):
        all_matches = 0
        all_totals = 0
        for node1_devID in nodelist1:
            for node2_devID in nodelist2:
                if node1_devID == node2_devID:
                    continue
                #print("comparing {} and {}".format(node1_devID,node2_devID))
                matches, intervals, totals = get_matches_2_nodes(node1_devID, node2_devID, nodes)
                all_matches += sum(matches)
                all_totals += sum(totals)
                #plot_matches_2_nodes(node1.get_deviceID(),node2.get_deviceID(), nodes)
                #plt.pause(2)


        threshold_list.append(threshold)
        match_list.append(all_matches)
        totals_list.append(all_totals)

    return threshold_list, match_list, totals_list


if __name__ == "__main__":
    print("Running main")


    data_path = "data_Feb09_difrms" # "26Jan_testing - phones" "data_Jan23_all"
    device_list = get_devIDs(data_path)

    try:
        f = open('saved_vars\\data_Feb09_difrms_nodes','rb')
        nodes = pickle.load(f)
    except:
        print("Pickle file not found, building nodes")
        nodes = get_nodes()
        f = open('saved_vars\\data_Feb09_difrms_nodes', 'wb')
        pickle.dump(nodes,f)
        f.close()



    print("device list: {}".format(device_list))

    BSSID_list = nodes[0].get_master_AP_list()["BSSID_list"]




#*********************** Different ROOMS comparison Feb09_data **********************
    # device_list: ['3c6105d41631', 'e8db84c4c0b0', '3c6105d37067', 'e8db84c4c80a', '3c6105d49ef8',
    #  '3c6105d37f73', 'e8db84c62200', '3c6105d3a726', 'e8db84c620b1']

    threshold = 53
    interval = 10
    scatters = []

    fig, ax = plt.subplots()

    # plot all

    try:
        f = open('saved_vars\\data_Feb09_difrms_thresh_res_all','rb')
        res, threshold_list, match_list, totals_list = pickle.load(f)
    except:
        print("Pickle file not found, getting thresh_res_all")
        threshold_list, match_list, totals_list = threshold_pair_comparison(device_list, device_list, nodes)
        res = [i / j for i, j in zip(match_list, totals_list)]
        f = open('saved_vars\\data_Feb09_difrms_thresh_res_all', 'wb')
        pickle.dump((res, threshold_list, match_list, totals_list),f)
        f.close()

    print("res_all")
    for i in res:
        print(i)

    scatter = ax.scatter(threshold_list, res, label="diff_rm_All", marker=".")
    scatters.append(scatter)



    # this one is suspect
    # plot 7067_c0b0-a726 in basement by living room tv and a726 in basement guest bedroom

    try:
        f = open('saved_vars\\data_Feb09_difrms_thresh_7067_c0b0-a726','rb')
        res, threshold_list, match_list, totals_list = pickle.load(f)
    except:
        print("Pickle file not found, getting 7067_c0b0-a726")
        threshold_list, match_list, totals_list = threshold_pair_comparison(
            ['3c6105d37067','e8db84c4c0b0'],['3c6105d3a726'], nodes)
        res = [i / j for i, j in zip(match_list, totals_list)]
        f = open('saved_vars\\data_Feb09_difrms_thresh_7067_c0b0-a726', 'wb')
        pickle.dump((res, threshold_list, match_list, totals_list),f)
        f.close()

    print("7067_c0b0-a726 basmnt_lvr2tv ")
    for i in res:
        print(i)

    scatter = ax.scatter(threshold_list, res, label="basmnt_lvr2tv", marker=".")
    scatters.append(scatter)



    # plot 7067+c0b0-c80a  basement tv to masterBR closet

    try:
        f = open('saved_vars\\data_Feb09_difrms_thresh_7067+c0b0-c80a','rb')
        res, threshold_list, match_list, totals_list = pickle.load(f)
    except:
        print("Pickle file not found, getting 7067+c0b0-c80a")
        threshold_list, match_list, totals_list = threshold_pair_comparison(
            ['3c6105d37067','e8db84c4c0b0'],['e8db84c4c80a'], nodes)
        res = [i / j for i, j in zip(match_list, totals_list)]
        f = open('saved_vars\\data_Feb09_difrms_thresh_7067+c0b0-c80a', 'wb')
        pickle.dump((res, threshold_list, match_list, totals_list),f)
        f.close()

    print("7067+c0b0-c80a bsmnTV2mstrclst")
    for i in res:
        print(i)

    scatter = ax.scatter(threshold_list, res, label="bsmnTV2mstrclst", marker=".")
    scatters.append(scatter)

    # plot c80a-2200+9ef8  kitchen to master bedroom closet

    try:
        f = open('saved_vars\\data_Feb09_difrms_thresh_c80a-2200+9ef8','rb')
        res, threshold_list, match_list, totals_list = pickle.load(f)
    except:
        print("Pickle file not found, getting c80a-2200+9ef8")
        threshold_list, match_list, totals_list = threshold_pair_comparison(
            ['e8db84c4c80a'],['e8db84c62200','3c6105d49ef8'], nodes)
        res = [i / j for i, j in zip(match_list, totals_list)]
        f = open('saved_vars\\data_Feb09_difrms_thresh_c80a-2200+9ef8', 'wb')
        pickle.dump((res, threshold_list, match_list, totals_list),f)
        f.close()

    print("c80a-2200+9ef8 mstrclst2kitchen")
    for i in res:
        print(i)

    scatter = ax.scatter(threshold_list, res, label="mstrclst2ktchn", marker=".")
    scatters.append(scatter)

    # plot 2200+9ef8-a726  ktchn to basment bdrm

    try:
        f = open('saved_vars\\data_Feb09_difrms_thresh_2200+9ef8-a726','rb')
        res, threshold_list, match_list, totals_list = pickle.load(f)
    except:
        print("Pickle file not found, getting 2200+9ef8-a726")
        threshold_list, match_list, totals_list = threshold_pair_comparison(
            ['e8db84c62200','3c6105d49ef8'],['3c6105d3a726'], nodes)
        res = [i / j for i, j in zip(match_list, totals_list)]
        f = open('saved_vars\\data_Feb09_difrms_thresh_2200+9ef8-a726', 'wb')
        pickle.dump((res, threshold_list, match_list, totals_list),f)
        f.close()

    print("2200+9ef8-a726 kitchen2bsmbrdm")
    for i in res:
        print(i)

    scatter = ax.scatter(threshold_list, res, label="kitchen2bsmbrdm", marker=".")
    scatters.append(scatter)

    # plot 7067+c0b0-2200+9ef8  bsmnttv 2 kitcn

    try:
        f = open('saved_vars\\data_Feb09_difrms_thresh_7067+c0b0-2200+9ef8','rb')
        res, threshold_list, match_list, totals_list = pickle.load(f)
    except:
        print("Pickle file not found, getting 7067+c0b0-2200+9ef8")
        threshold_list, match_list, totals_list = threshold_pair_comparison(
            ['3c6105d37067','e8db84c4c0b0'],['e8db84c62200','3c6105d49ef8'], nodes)
        res = [i / j for i, j in zip(match_list, totals_list)]
        f = open('saved_vars\\data_Feb09_difrms_thresh_7067+c0b0-2200+9ef8', 'wb')
        pickle.dump((res, threshold_list, match_list, totals_list),f)
        f.close()

    print("7067+c0b0-2200+9ef8 bsmtv2ktchn")
    for i in res:
        print(i)

    scatter = ax.scatter(threshold_list, res, label="bsmnttv2ktchn", marker=".")
    scatters.append(scatter)


    # plot Jan23_all  control for all

    try:
        f = open('saved_vars\\data_Jan23_thresh_Jan23_all','rb')
        res, threshold_list, match_list, totals_list = pickle.load(f)
    except:
        print("Pickle file not found, getting Jan23_all")
        data_path = "data_Jan23_all"  # "26Jan_testing - phones" "data_Jan23_all"
        device_list = get_devIDs(data_path)
        nodes = get_nodes()
        threshold_list, match_list, totals_list = threshold_pair_comparison(device_list, device_list, nodes)
        res = [i / j for i, j in zip(match_list, totals_list)]
        f = open('saved_vars\\data_Jan23_thresh_Jan23_all', 'wb')
        pickle.dump((res, threshold_list, match_list, totals_list),f)
        f.close()

    print("Jan23_all")
    for i in res:
        print(i)

    scatter = ax.scatter(threshold_list, res, label="Jan23_all", marker=".")
    scatters.append(scatter)


    plt.title("Threshold Matches")
    ax.legend(handles=scatters, loc="lower right", title="datasets")
    plt.show()



    for a,b,c in zip(threshold_list,match_list,totals_list):
        print(a,b,c)

#******************************************************************************************************




