from datetime import datetime
import sys
from io import StringIO
import pandas as pd
import re
import numpy as np

f = open(sys.argv[1])
timeStep = 60

min = 1

tops = f.read().split("\2022-07\n")
print(len(tops))

gsToTime = {}

for top in tops: 
    lines = top.split("\n")
    if (len(lines) < 3):
        continue
    time = lines[0]
    time = datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
    print("time", time)

    gsCount = {}

    for line in lines[1:]:    
        if line == 'end of available map':
            break
        sat = int(line[:line.index(":")][:-1])

        trueGs = re.findall('(\d+)\sTrue', line)
        #print(trueGs)

        for gs in trueGs:
            gsInd = int(gs)
            #print(gsInd)
            if gsInd in gsCount:
                gsCount[gsInd] += 1
            else:
                gsCount[gsInd] = 1

    for gs, count in gsCount.items():
        if count == min:
            if gs in gsToTime:
                gsToTime[gs] += timeStep
            else:
                gsToTime[gs] = timeStep


# use overallLog to get the locations of the GSs
import overallLog
gsToLoc = {}
for row in overallLog.get_str("../log", "Node Created"):
    gsToLoc[int(row['nodeId'])] = (float(row['idx3']), float(row['idx4']))

# make cartopy plot of the GSs with the time they were in view of one satellite
import cartopy # type: ignore
import cartopy.crs as ccrs # type: ignore
from cartopy.geodesic import Geodesic # type: ignore
import matplotlib.pyplot as plt # type: ignore

fig = plt.figure(figsize=(10, 10))
ax = plt.axes(projection=ccrs.PlateCarree())
ax.set_global()
ax.coastlines()
ax.stock_img()

for gs, time in gsToTime.items():
    loc = gsToLoc[gs]
    #plot it with a color based on the time
    ax.plot(loc[0], loc[1], 'o', color=(time/3600, 0, 0), markersize=10)

plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.title("Time in view of one satellite")
plt.savefig("timeInOne.png")
