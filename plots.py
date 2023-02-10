from analysis import *

# help file just to simplify and produce all the plots

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
    matches,intervals,totals = get_matches_2_nodes(devID1,devID2,nodes)
    plot_matches(matches,intervals,"",ax)
    plt.title("Matches between {} and {}".format(devID1,devID2))
    print(matches,intervals,totals)
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


if __name__ == "__main__":
    print("Running main")
    data_path = "data_Jan23_all" #"data_Feb09_difrms" # "26Jan_testing - phones" "data_Jan23_all"
    device_list = get_devIDs(data_path)

    nodes = get_nodes()

    # node = rxnode("HTC")
    # node.import_data_wigle('26Jan_testing - phones\\HTC.csv')
    # plot_all_APs_node(node)
    # nodes.append(node)
    # node = rxnode("axon7")
    # node.import_data_wigle('26Jan_testing - phones\\axon7.csv')
    # plot_all_APs_node(node)
    # nodes.append(node)
    # node = rxnode("tracfone")
    # node.import_data_wigle('26Jan_testing - phones\\tracfone.csv')
    # plot_all_APs_node(node)
    # nodes.append(node)
    # device_list.append("HTC")
    # device_list.append("axon7")
    # device_list.append("tracfone")

    print("device list: {}".format(device_list))




    # print("node[0].get_data(): {}".format(nodes[0].get_data()))
    # print("node[0].get_data2(): {}".format(nodes[0].get_data2()))

    BSSID_list = nodes[0].get_master_AP_list()["BSSID_list"]

# TODO subplots with these other devices from the newest data set
# data quality isn't great for these..
#     plot_matches_2_nodes("axon7", "HTC", nodes)
#     plt.pause(1)
#     plot_matches_2_nodes("HTC", "tracfone", nodes)
#     plt.pause(1)
#     plot_matches_2_nodes("tracfone", "axon7", nodes)
#     plt.pause(4)

    all_matches = 0
    all_totals = 0
    for node1 in nodes:
        for node2 in nodes:
            if node1==node2:
                continue
            matches, intervals, totals = get_matches_2_nodes(node1.get_deviceID(),node2.get_deviceID(), nodes)
            all_matches += sum(matches)
            all_totals += sum(totals)
            plot_matches_2_nodes(node1.get_deviceID(),node2.get_deviceID(), nodes)
            plt.pause(2)

    print("All matches/totals for:")
    print(all_matches,all_totals)


#*********************** Different ROOMS comparison Feb09_data **********************
# device list: ['3c6105d41631', 'e8db84c4c0b0', '3c6105d37067', 'e8db84c4c80a', '3c6105d49ef8',
    # '3c6105d37f73', 'e8db84c62200', '3c6105d3a726', 'e8db84c620b1']

    threshold = 53
    interval = 10


    for threshold in range(1,50):
        all_matches = 0
        all_totals = 0
        # for node1 in nodes:
        #     for node2 in nodes:
        #         if node1==node2:
        #             continue
        #         matches, intervals, totals = get_matches_2_nodes(node1.get_deviceID(),node2.get_deviceID(), nodes)
        #         all_matches += sum(matches)
        #         all_totals += sum(totals)

        matches, intervals, totals = get_matches_2_nodes('3c6105d37067','e8db84c4c80a', nodes)
        all_matches += sum(matches)
        all_totals += sum(totals)
        matches, intervals, totals = get_matches_2_nodes('e8db84c4c0b0','e8db84c4c80a', nodes)
        all_matches += sum(matches)
        all_totals += sum(totals)

                #plot_matches_2_nodes(node1.get_deviceID(),node2.get_deviceID(), nodes)
                #plt.pause(2)

        #print("All matches/totals for:")
        print(threshold,all_matches,all_totals)

#******************************************************************************************************


    # for node1 in nodes:
    #     node1.print_num_APs()

    # Matching nodes
    # maybe check for missing intervals, create another list and include a number for how many measurements were in that

    # for node1 in nodes:
    #     fig, ax = plt.subplots()
    #     for node2 in nodes:
    #         if node1==node2:
    #             continue
    #         matches,intervals = match_all_APs3(node1,node2,threshold=30,interval=20)
    #         #print("Comparing dev {} and dev {}".format(node1.get_deviceID(),node2.get_deviceID()))
    #         #print(matches)
    #         #print(intervals)
    #         plot_matches(matches,intervals,"",ax)
    #     fig.show()
    #     plt.pause(4)
    #     plt.close()

    # ---plot measurements per AP
    fig, ax = plt.subplots()
    for BSSID in BSSID_list:
        plot_AP_across_devices(nodes ,BSSID)