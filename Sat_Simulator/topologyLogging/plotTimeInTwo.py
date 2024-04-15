from datetime import datetime
import sys
from io import StringIO
import pandas as pd
import re
import numpy as np

f = open(sys.argv[1])
timeStep = 60

min = 1

tops = f.read().split("\nEND TOPOLOGY\n")
gsToTime = {}

for top in tops: 
    lines = top.split("\n")
    if (len(lines) < 3):
        continue
    time = lines[0]
    time = datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
    print(time)

    gsCount = {}

    for line in lines[1:]:    
        if line == 'end of available map':
            break
        sat = int(line[:line.index(":")])
        
        trueGs = re.findall('(\d+)\sTrue', line)
        
        for gs in trueGs:
            gsInd = int(gs)
            if gsInd in gsCount:
                gsCount[gsInd] += 1
            else:
                gsCount[gsInd] = 1

    for gs, count in gsCount.items():
        if count >= min:
            if gs in gsToTime:
                gsToTime[gs] += timeStep
            else:
                gsToTime[gs] = timeStep
print(len(gsToTime))

latStr = [str(i) for i in gsToTime.values()]

import matplotlib.pyplot as plt
num_bins = 100
linewidth = 5
lst = list(gsToTime.values())
lst.sort()
counts, bin_edges = np.histogram (lst, bins=num_bins, density=True)
cdf = np.cumsum (counts)
print(cdf)
ax = plt.axes()
ax.plot (bin_edges[1:],cdf/cdf[-1],'b:',linewidth=linewidth)
ax.tick_params(axis='both', which='major',labelsize=18)
ax.legend(fontsize=18, loc='lower right')
ax.set_xlabel('Time Spent In Greater Than Two Footprints (s)',fontsize=18)
ax.set_ylabel('Count',fontsize=18)
plt.tight_layout()
plt.savefig("plots/timeInTwo.png")
