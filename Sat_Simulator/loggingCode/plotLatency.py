#usage: python plotLatency.py [log.txt]
import matplotlib.pyplot as plt
import sys
import numpy as np
import overallLog
import cartopy # type: ignore
import cartopy.crs as ccrs # type: ignore
from cartopy.geodesic import Geodesic # type: ignore

fileName = sys.argv[1]

dataToPackets = {}
packetsToData = {}
dataToTime = {}
dataToNode = {}

latencys = []
latsAndPackets = []

nodes = {}
nodeToHighestLat = {}

for row in overallLog.get_str(fileName, "Node Created"):
    if float(row["idx5"]) >= -0.0:
        nodes[row["nodeId"]] = ( float(row["idx3"]), float(row["idx4"]))
        nodeToHighestLat[row['nodeId']] = -1

for row in overallLog.get_str(fileName, "Data Created By"):
    dataToTime[row['dataId']] = row['time']
    dataToNode[row['dataId']] = row['nodeId']

for row in overallLog.get_str(fileName, "Packet Created by "):
    packetId = row['packetId']
    dataId = row['dataId']

    packetsToData[packetId] = dataId
    dataToPackets[packetId] = packetId

recievedPackets = {}
for row in overallLog.get_str(fileName, "Iot Recieved packet:"):
    packetId = row['packetId']
    if packetId in recievedPackets.keys():
        continue
    else:
        recievedPackets[packetId] = True
    dataId = packetsToData[packetId]
    creationTime = dataToTime[dataId]
    receptionTime = row['time']

    lat = (receptionTime - creationTime).total_seconds()
    latencys.append(lat)

    nodeId = dataToNode[dataId]

    #nodeToHighestLat[nodeId] = max( lat, nodeToHighestLat[nodeId])

    latsAndPackets.append((packetId, lat))


latsAndPackets.sort(key = lambda x : x[1])
latStr = [str(i) for i in latencys]

for i in latsAndPackets:
    print(i)

##Write it to csv:
#file = open(sys.argv[1].replace('.txt', 'cdf.csv'), 'w+')
#file.write(",".join(latStr))
#file.close()

###CDF graph:
num_bins = 100
linewidth = 5
counts, bin_edges = np.histogram (latencys, bins=num_bins, density=True)
cdf = np.cumsum (counts)

ax = plt.axes()
ax.plot (bin_edges[1:]/1000,cdf/cdf[-1],'b:',linewidth=linewidth,label='Latencies (1000 s) ')
ax.tick_params(axis='both', which='major',labelsize=18)
ax.legend(fontsize=18, loc='lower right')
ax.set_xlabel('Packet Latency',fontsize=18)
ax.set_ylabel('CDF',fontsize=18)
plt.savefig('plots/latency.png')
plt.close('all')

"""
##Map of latencys:
fig = plt.figure()
map = ccrs.PlateCarree()
ax = fig.add_subplot(projection=map)
ax.coastlines()

longs = []
lats = []
highestLats = []

for node in nodeToHighestLat.keys():
    if nodeToHighestLat[node] != -1:
        lat, long = nodes[node]
        longs.append(long)
        lats.append(lat)
        highestLats.append( nodeToHighestLat[node] )

highestLats = np.array(highestLats)
plt.scatter(x = longs, y = lats, transform=map, c = highestLats/1000, cmap='YlGn')
plt.colorbar(label="Highest Latency (s)")
plt.savefig("plots/latMap.png")
"""