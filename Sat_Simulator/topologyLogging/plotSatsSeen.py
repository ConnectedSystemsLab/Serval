from datetime import datetime
import sys
from io import StringIO
import pandas as pd
import re

f = open(sys.argv[1])
timeStep = 60


tops = f.read().split("\nEND TOPOLOGY\n")
gsToTimes = {}

for top in tops: 
    lines = top.split("\n")
    if (len(lines) < 3):
        continue
    time = lines[0]
    time = datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
    print(time)

    for line in lines[1:]:    
        if line == 'end of available map':
            break
        sat = int(line[:line.index(":")])
        
        trueGs = re.findall(',[^,]+?True', line)
        
        for gs in trueGs:
            gsInd = int(gs[1:gs.index("True")])
            if gsInd in gsToTimes:
                if time in gsToTimes[gsInd]:
                    gsToTimes[gsInd][time].append(sat)
                else:
                    gsToTimes[gsInd][time] = [sat]
            else:
                gsToTimes[gsInd] = {}
                gsToTimes[gsInd][time] = [sat]

from itertools import groupby
from operator import itemgetter

contactLengths = []                                
counts = []
for gs, timeToSat in gsToTimes.items():
    lastTime = None
    time = 0
    times = list(timeToSat.keys())
    times.sort()
    print(times)    
    minutesToTimes = { (t - datetime(1970, 1, 1)).total_seconds() // timeStep : t for t in times }
    print(minutesToTimes)
    for k, g in groupby(enumerate(minutesToTimes.keys()), lambda ix : ix[0] - ix[1]):
        keys = list(map(itemgetter(1), g))
        length = (keys[-1] - keys[0] + 1) * timeStep
        
        sats = set()
        for min in keys:
            for sat in timeToSat[minutesToTimes[min]]:
                sats.add(sat)
        print(sats)
        contactLengths.append(length)
        counts.append(len(sats))
        
import matplotlib.pyplot as plt
plt.scatter(contactLengths, counts)
plt.xlabel("Length of Continuous Contact (s)")
plt.ylabel("Number of Sats Seen During Contact")
plt.savefig("plots/allContact.png")
