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
            if gsInd not in gsToTimes:
                gsToTimes[gsInd] = []
            gsToTimes[gsInd].append(time)
from itertools import groupby
from operator import itemgetter

#you want to find out how long between when a gs stops seeing a sat and when it starts seeing a sat again
#so you want to find any gaps in the the dictionary of times that a gs sees a sat
#then you want to find the length of the gap


gapLengths = []
for gs, times in gsToTimes.items():
    times.sort()
    #find out how long between when a gs stops seeing a sat and when it starts seeing a sat again
    #so you want to find any gaps in the the dictionary of times that a gs sees a sat
    #then you want to find the length of the gap
    lastTime = None
    for time in times:
        if lastTime is not None:
            if (time - lastTime).total_seconds() > timeStep:
                gapLengths.append((time - lastTime).total_seconds())
        lastTime = time

import matplotlib.pyplot as plt
import numpy as np

plt.hist(gapLengths, bins=100)
print(np.mean(gapLengths), np.median(gapLengths))
plt.savefig("gapLengths.png")