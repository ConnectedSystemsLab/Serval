##usage: python plotMemory.py logfile

import sys
from statistics import mean
import matplotlib.pyplot as plt
from datetime import datetime
import overallLog
import cartopy # type: ignore
import cartopy.crs as ccrs # type: ignore
from cartopy.geodesic import Geodesic # type: ignore
import numpy as np


#2022-07-13 21:54:00,Iot Memory,0
timesD = {}

nodes = {}
nodeToHighestBuffer = {}

for row in overallLog.get_str(sys.argv[1], "Node Created"):
    nodes[row["nodeId"]] = ( float(row["idx3"]), float(row["idx4"]))
    if float(row["idx5"]) >= -0.0:
        nodes[row["nodeId"]] = ( float(row["idx3"]), float(row["idx4"]))

for row in overallLog.get_str(sys.argv[1], "Iot Memory"):
    time = row['time']
    val = int(row['idx2'])
    if time in timesD.keys():
        timesD[time].append(val)
    else:
        timesD[time] = [val]
    node = row["nodeId"]
    if node in nodeToHighestBuffer:
        nodeToHighestBuffer[node] = max( val, nodeToHighestBuffer[node])
    else: 
        nodeToHighestBuffer[node] = val

avgs = []
maxs = []
times = []
for key, val in timesD.items():
    avgs.append(mean(val))
    maxs.append(max(val))
    times.append(key)

fig = plt.figure()
plt.plot_date(times, avgs, label="Average")
plt.plot_date(times, maxs, label="Max")
plt.title("Length of Iot Packet Buffers")
plt.legend()
fig.autofmt_xdate()
plt.savefig("plots/iotmem.png")

fig = plt.figure()
map = ccrs.PlateCarree()
ax = fig.add_subplot(projection=map)
ax.coastlines()
ax.set_extent([-130, -60, 20, 50])

longs = []
lats = []
highestVals = []

for node in nodeToHighestBuffer.keys():
    if nodeToHighestBuffer[node] != -1:
        lat, long = nodes[node]
        longs.append(long)
        lats.append(lat)
        highestVals.append( nodeToHighestBuffer[node] )

highestVals = np.array(highestVals)
inds = np.argpartition(highestVals, -10)[-10:]

plt.scatter(x = np.array(longs)[inds], y = np.array(lats)[inds], transform=map, c = highestVals[inds], cmap='YlGn')
plt.colorbar(label="Length of Iot Packet Queue")
plt.savefig("plots/bufferMap.png")

