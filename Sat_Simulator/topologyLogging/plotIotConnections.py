from datetime import datetime
import sys
from io import StringIO
import pandas as pd
import re
import matplotlib.pyplot as plt

f = open(sys.argv[1])
tops = f.read().split("\nEND TOPOLOGY\n")

times = []
counts = []
min = 4

for top in tops: 
    lines = top.split("\n")
    if (len(lines) < 3):
        continue
    time = lines[0]
    time = datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
    print(time) 
    
    gsToSat = {}
    for line in lines[1:]:    
        if line == 'end of available map':
            break
        sat = int(line[:line.index(":")])
        
        trueGs = re.findall(',[^,]+?True', line)
        
        for gs in trueGs:
            gsInd = int(gs[1:gs.index("True")])
            if gsInd in gsToSat:
                gsToSat[gsInd].append(sat)
            else:
                gsToSat[gsInd] = [sat]
    cnt = 0
    for gs, list in gsToSat.items():
        if len(list) >= min:
            cnt += 1
    times.append(time)
    counts.append(cnt)
    
plt.plot_date(times, counts)
plt.xlabel("Time in Simulation")
plt.ylabel("Number of Iot Devices That Can See More Than " + str(min) + " Sats")
plt.savefig("timeInContact.png")
