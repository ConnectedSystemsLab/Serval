from datetime import datetime
import sys
from io import StringIO
import pandas as pd
import re

f = open(sys.argv[1])
tops = f.read().split("\nEND TOPOLOGY\n")
sTimes = {}

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
            tup = (sat, gsInd)
            print(tup)
            if tup in sTimes:
                sTimes[tup].append(time)
            else:
                sTimes[tup] = [time]

times = []                                
for key, list in sTimes.items():
    lastTime = None
    time = 0
    for currTime in list:
        if lastTime is None:
            time = 60
            lastTime = currTime
        else:
            if (currTime - lastTime).total_seconds() <= 60:
                lastTime = currTime
                time += 60
            else:
                lastTime = currTime
                times.append(time)
                time = 60
    times.append(time)

import matplotlib.pyplot as plt
plt.hist(times, align="left")
plt.xlabel("Length of Contact (s)")
plt.ylabel("Frequency")
plt.savefig("timeInContact.png")
