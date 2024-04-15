from datetime import datetime
import sys
from io import StringIO
import pandas as pd
import re
import numpy as np
import matplotlib.pyplot as plt

f = open(sys.argv[1])
timeStep = 60
tops = f.read().split("\nEND TOPOLOGY\n")
for min in range(1, 10):
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

    num_bins = 100
    linewidth = 5
    lst = list(gsToTime.values())
    lst.sort()
    counts, bin_edges = np.histogram (lst, bins=num_bins, density=True)
    cdf = np.cumsum (counts)
    print(cdf)
    plt.plot (bin_edges[1:],cdf/cdf[-1],linewidth=linewidth, label=str(min) + " satellites")

plt.tick_params(axis='both', which='major', labelsize=18)

#legend to the top right outside the plot
plt.legend(loc='upper left', fontsize=18, bbox_to_anchor=(1,1))
plt.xlabel('Time Spent In N Footprints (s)',fontsize=18)
plt.ylabel('Count',fontsize=18)
plt.tight_layout()
plt.savefig("plots/timeInTwo.png")
