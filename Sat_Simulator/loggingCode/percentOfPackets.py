#usage: python percentOfPackets.py [log.txt]
import matplotlib.pyplot as plt
#this will create a graph of the percent of packets recieved from each node
# Path: loggingCode/percentOfPackets.py
#usage: python percentOfPackets.py [log.txt]
# [log.txt] should be of the form: [alpha].txt where alpha is a float
import sys


import matplotlib.pyplot as plt
import sys
import numpy as np
import overallLog
import cartopy # type: ignore
import cartopy.crs as ccrs # type: ignore
from cartopy.geodesic import Geodesic # type: ignore

for fileName in sys.argv[1:]:
    dataToNode = {}
    packetToNode = {}
    nodeToSuccess = {}
    nodeToTotal = {}
    packetToRecieved = {}
    nodes = {}

    for row in overallLog.get_str(fileName, "Node Created"):
        if float(row["idx5"]) >= -10:
            nodes[row["nodeId"]] = ( float(row["idx3"]), float(row["idx4"]))
            nodeToSuccess[row['nodeId']] = 0
            nodeToTotal[row['nodeId']] = 0

    for row in overallLog.get_str(fileName, "Data Created By"):
        for key in row.keys():
            if "dataId" in key:
                dataToNode[row[key]] = row['nodeId']
    
    for row in overallLog.get_str(fileName, "Packet Created by "):
        if 'dataId' not in row.keys():
            continue
        dataId = row['dataId']
        nodeId = dataToNode[dataId]
        packetToNode[row['packetId']] = nodeId
        nodeToTotal[nodeId] += 1
        packetToRecieved[row['packetId']] = False
    
    for row in overallLog.get_str(fileName, "Packet recieved by sat"):
        if packetToRecieved[row['packetId']]:
            continue
        packetId = row['packetId']
        nodeId = packetToNode[packetId]
        nodeToSuccess[nodeId] += 1
        packetToRecieved[packetId] = True

    #now we have the data, lets plot it as a cdf graph
    successes = []
    totals = []
    for node in nodeToSuccess.keys():
        if nodeToTotal[node] == 0:
            continue
        successes.append(nodeToSuccess[node])
        totals.append(nodeToTotal[node])

    successes = np.array(successes)
    totals = np.array(totals)

    percentages = successes/totals

    #create a cdf graph
    num_bins = 100
    linewidth = 5
    counts, bin_edges = np.histogram (percentages, bins=num_bins, density=True)
    cdf = np.cumsum (counts)

    plt.plot (bin_edges[1:], cdf/cdf[-1], linewidth=linewidth, label=fileName)

#move the legend to the top left outside the plot
plt.legend(loc='upper left', bbox_to_anchor=(1,1))
plt.xlabel('Percent of Packets Recieved For Each Device',fontsize=18)
plt.ylabel('CDF',fontsize=18)
plt.tight_layout()
plt.savefig("plots/percentOfPackets.png")
plt.show()
