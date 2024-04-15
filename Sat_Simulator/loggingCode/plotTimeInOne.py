from datetime import datetime
import sys
from io import StringIO
import re

f = open(sys.argv[1])
timeStep = 60

numWanted = 5

#tops = f.read().split("\nEND TOPOLOGY\n")
tops = f.read().split("2022-07")
print(len(tops))
gsToTime = {}
for top in tops:
    #if i == 100:
    #    break
    #i += 1 
    lines = top.split("\n")
    if (len(lines) < 3):
        continue
    time = lines[0]
    time = datetime.strptime(time, "-%d %H:%M:%S")
    time = time.replace(year=2022)
    time = time.replace(month=7)
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
        if count >= numWanted:
            if gs in gsToTime:
                gsToTime[gs] += timeStep
            else:
                gsToTime[gs] = timeStep

print(gsToTime.values())
# use overallLog to get the locations of the GSs
import overallLog
gsToLoc = {}

for row in open("../info").readlines():
    #row is id (lat, long, alt)
    row = row.split()
    gsToLoc[int(row[0])] = (float(row[1][1:-1]), float(row[2][:-1]))
#make a cartopy plot of the GSs with the time they were in view of one satellite
# make a colorbar for the time
import cartopy # type: ignore
import cartopy.crs as ccrs # type: ignore
from cartopy.geodesic import Geodesic # type: ignore
import matplotlib.pyplot as plt # type: ignore
import matplotlib.colors as colors # type: ignore
import matplotlib.cm as cmx # type: ignore

fig = plt.figure(figsize=(10, 10))
ax = plt.axes(projection=ccrs.PlateCarree())
ax.set_global()
ax.stock_img()
ax.coastlines()

# make a colorbar
jet = plt.get_cmap('jet')
lst = list(gsToTime.values())
cNorm  = colors.Normalize(vmin=min(lst), vmax=max(lst))
scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=jet)

for gs, time in gsToTime.items():
    loc = gsToLoc[gs]
    colorVal = scalarMap.to_rgba(time)
    ax.plot(loc[1], loc[0], marker='o', color=colorVal, transform=ccrs.PlateCarree())

# make a colorbar
sm = plt.cm.ScalarMappable(cmap=jet, norm=cNorm)
sm._A = []
cbar = plt.colorbar(sm)
cbar.set_label('Time in view of five or greater satellites (s)')
plt.title('Time in view of five or greater satellites')
plt.savefig('timeGreaterThan5.png')
