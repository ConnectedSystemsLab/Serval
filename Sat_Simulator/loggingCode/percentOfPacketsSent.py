#usage: python plotLatency.py [log.txt]
import matplotlib.pyplot as plt
#this will create a graph of the percent of packets recieved from each node
# Path: loggingCode/percentOfPackets.py
#usage: python plotLatency.py [log.txt]
# [log.txt] should be of the form: [alpha].txt where alpha is a float
import sys


import matplotlib.pyplot as plt
import sys
import numpy as np
import overallLog
import cartopy # type: ignore
import cartopy.crs as ccrs # type: ignore
from cartopy.geodesic import Geodesic # type: ignore


print(sys.argv[1:])
for fileName in sys.argv[1:]:

    dataToNode = {}
    packetToNode = {}
    nodeToSuccess = {}
    nodeToTotal = {}
    packetToRecieved = {}
    nodes = {}
        
    def node_callback(row):
        if float(row["idx5"]) >= -10:
            nodes[row["nodeId"]] = ( float(row["idx3"]), float(row["idx4"]))
            nodeToSuccess[row['nodeId']] = 0
            nodeToTotal[row['nodeId']] = 0

    def data_callback(row):
        for key in row.keys():
            if "dataId" in key:
                dataToNode[row[key]] = row['nodeId']

    def packet_callback(row):
        if 'dataId' not in row.keys():
            return
        dataId = row['dataId']
        nodeId = dataToNode[dataId]
        packetToNode[row['packetId']] = nodeId
        nodeToTotal[nodeId] += 1
        packetToRecieved[row['packetId']] = False

    def sending_callback(row):
        if "IoT" in row['nodeName']:    
            nodeToTotal[row['nodeId']] += 1
            packetToRecieved[row['packetId']] = False

    def packet_recieved_callback(row):
        if packetToRecieved[row['packetId']]:
            return
        packetId = row['packetId']
        nodeId = packetToNode[packetId]
        nodeToSuccess[nodeId] += 1
        packetToRecieved[packetId] = True


    overallLog.get_str_with_callback(fileName, "Node Created", node_callback)
    overallLog.get_str_with_callback(fileName, "Data Created By", data_callback)
    overallLog.get_str_with_callback(fileName, "Packet Created By", packet_callback)
    overallLog.get_str_with_callback(fileName, "Packet recieved by sat", packet_recieved_callback)
        

    #now we have the data, lets plot it as a cdf graph
    successes = []
    totals = []
    for node in nodeToSuccess.keys():
        if nodeToTotal[node] == 0:
            continue
        successes.append(nodeToSuccess[node])
        totals.append(nodeToTotal[node])

    successes = np.array(successes)
    print("Total Successes:", successes.sum())
    totals = np.array(totals)
    print("Total Totals:", totals.sum())
    print("Percent Success:", successes.sum()/totals.sum())

    percentages = successes/totals

    #create a cdf graph
    num_bins = 100
    linewidth = 5
    counts, bin_edges = np.histogram (percentages, bins=num_bins, density=True)
    cdf = np.cumsum (counts)

    plt.plot (bin_edges[1:], cdf/cdf[-1], linewidth=linewidth, label=fileName)

#move the legend to the top left outside the plot
plt.legend(loc='upper left', bbox_to_anchor=(1,1))
plt.xlabel('Recieved Packets/Packets Sent For Each Device',fontsize=18)
plt.ylabel('CDF',fontsize=18)
#plt.title("Alpha: " + str(alpha))
plt.title("Distribution of Percent of Packets")
plt.tight_layout()
plt.savefig("plots/percentOfPackets.png")
plt.show()
