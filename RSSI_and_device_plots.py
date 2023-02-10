from analysis import *
import pickle
import matplotlib as mpl
import numpy as np

# This is a helper file to produce the match % vs RSSI threshold graphs

threshold = 20
interval = 30
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

def plot_matches_formatted(matches,intervals,totals,devID="?",ax=None):
    scatters = []

    scatter = ax.scatter(intervals, totals, label="Max Possible", marker="o")
    scatters.append(scatter)
    print(totals)

    scatter = ax.scatter(intervals, matches, label="Actual", marker=".")
    scatters.append(scatter)
    print(matches)



    plt.title("Device: {}".format(devID))
    ax.legend(handles=scatters, loc="lower right", title="Matches")




def plot_matches_2_nodes(devID1,devID2, nodes):
    fig,ax = plt.subplots()
    matches,intervals,totals = get_matches_2_nodes(devID1,devID2,nodes)
    plot_matches_formatted(matches,intervals,totals,"",ax)
    title = "Devices: {},{} - RSSI Threshold: {}".format(devID1[8:],devID2[8:],threshold)
    plt.title(title)
    plt.xlabel("Time")
    plt.ylabel("Number of Matches")

    plt.tick_params(
        axis='x',  # changes apply to the x-axis
        which='both',  # both major and minor ticks are affected
        bottom=False,  # ticks along the bottom edge are off
        top=False,  # ticks along the top edge are off
        labelbottom=False)  # labels along the bottom edge are off
    ax.set_yticks([0,2,4,6,8,10,12,14,16,18,20])
    filename = "Devices{}-{}_RSSI{}".format(devID1[8:],devID2[8:],threshold) + ".png"
    plt.savefig(filename,dpi=300)
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

    plt.xlabel("Time")

    plt.tick_params(
        axis='x',  # changes apply to the x-axis
        which='both',  # both major and minor ticks are affected
        bottom=False,  # ticks along the bottom edge are off
        top=False,  # ticks along the top edge are off
        labelbottom=False)  # labels along the bottom edge are off

    plt.title("Device: {}".format(node.get_deviceID())[8:])
    #ax.legend(handles=scatters, loc="lower left", title="Matches")
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

    data_path = "data_Jan23_all"
    device_list = get_devIDs(data_path)


    try:
        f = open('saved_vars\\data_Jan23_all','rb')
        nodes = pickle.load(f)
    except:
        print("Pickle file not found, building nodes")
        data_path = "data_Jan23_all"
        nodes = get_nodes()
        f = open('saved_vars\\data_Jan23_all', 'wb')
        pickle.dump(nodes,f)
        f.close()

# ************************** Plot matches for nodes ****************************
    # pick just two representative samplmes to compare
    # good performing: c0b0 and a726
    # bad performing: 7067 and 20b1
    # ['3c6105d37067', 'e8db84c4c80a', 'e8db84c62200', '3c6105d41631', 'e8db84c620b1',
    # # '3c6105d37f73', 'e8db84c4c0b0', '3c6105d49ef8', '3c6105d3a726']

    pause_count = 0
    all_matches = 0
    all_totals = 0

    matches, intervals, totals = get_matches_2_nodes('e8db84c4c0b0','3c6105d3a726', nodes)
    plot_matches_2_nodes('e8db84c4c0b0','3c6105d3a726', nodes)

    matches, intervals, totals = get_matches_2_nodes('3c6105d37067','e8db84c620b1', nodes)
    plot_matches_2_nodes('3c6105d37067','e8db84c620b1', nodes)

    print("All matches/totals for:")
    print(all_matches,all_totals)




# *********************** plot all Aps for one node ***************************

    for node in nodes:
        # TODO: BSSID list doesn't seem to be right, use get_data().keys() instead..
        BSSID_list,_,_ = node.get_AP_list()
        print(len(node.get_data().keys()))
        print(len(BSSID_list))
        plot_all_APs_node(node)
        break

# ********************************************************************************



#*********************** Different ROOMS comparison Feb09_data **********************
    # device_list: ['3c6105d41631', 'e8db84c4c0b0', '3c6105d37067', 'e8db84c4c80a', '3c6105d49ef8',
    #  '3c6105d37f73', 'e8db84c62200', '3c6105d3a726', 'e8db84c620b1']

    threshold = 53
    interval = 10
    scatters = []

    grades=50
    vmax=12

    fig, ax = plt.subplots()
    cmap = plt.get_cmap('jet', grades) # number of gradations in colormap
    norm = mpl.colors.Normalize(vmin=0, vmax=vmax) # range of values for colormap
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    # fig.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap=cmap),
    #              cax=ax, orientation='horizontal', label='Some Units')
    cbar = plt.colorbar(sm, ticks=[0,1,2,3,4,5,6,7,8,9,10,11,12]) #np.linspace(0, 35,5,dtype="int")) # (start,end,=count)

    # plot all

    # don't need this one

    # try:
    #     f = open('saved_vars\\data_Feb09_difrms_thresh_res_all','rb')
    #     res, threshold_list, match_list, totals_list = pickle.load(f)
    # except:
    #     print("Pickle file not found, getting thresh_res_all")
    #     threshold_list, match_list, totals_list = threshold_pair_comparison(device_list, device_list, nodes)
    #     res = [i / j for i, j in zip(match_list, totals_list)]
    #     f = open('saved_vars\\data_Feb09_difrms_thresh_res_all', 'wb')
    #     pickle.dump((res, threshold_list, match_list, totals_list),f)
    #     f.close()
    #
    # print("res_all")
    # for i in res:
    #     print(i)
    #
    # # this one is a composite
    # scatter = ax.scatter(threshold_list, res, label="diff_rm_All", marker=".")
    # scatters.append(scatter)



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

    # this is about 25 ft - actually 31ft 9.45m
    scatter = ax.scatter(threshold_list, res, label="basmnt_lvr2tv~25", marker=".",c=cmap(9.45/vmax))
    #scatters.append(scatter)



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

    # this one is about 25 feet distance actual 24 ft 7.32m
    scatter = ax.scatter(threshold_list, res, label="bsmnTV2mstrclst~25", marker=".",c=cmap(7.32/vmax))
    #scatters.append(scatter)

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

    # this one is more than 30 ft actually 31 ft 9.45m
    scatter = ax.scatter(threshold_list, res, label="mstrclst2ktchn-30+", marker=".",c=cmap(9.45/vmax))
    #scatters.append(scatter)

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

    # less than 15 ft actual 14.5ft 4.42m
    scatter = ax.scatter(threshold_list, res, label="kitchen2bsmbrdm-15-", marker=".",c=cmap(4.42/vmax))
    #scatters.append(scatter)

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

    # more than 30 ft actual 35 ft 10.67m
    scatter = ax.scatter(threshold_list, res, label="bsmnttv2ktchn-30+", marker=".",c=cmap(10.67/vmax))
    #scatters.append(scatter)


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

    # should be 0.3m
    scatter = ax.scatter(threshold_list, res, label="Control Series", marker=".",c=cmap(0.3/vmax))
    scatters.append(scatter)
    plt.xlabel("RSSI Match Threshold (dB)")
    plt.ylabel("Ratio of Matches")
    plt.title("Indoor Threshold Comparison")
    cbar.set_label('Relative Distance (m)', rotation=270)
    ax.legend(handles=scatters, loc="lower right")
    plt.show()



    for a,b,c in zip(threshold_list,match_list,totals_list):
        print(a,b,c)

#******************************************************************************************************




