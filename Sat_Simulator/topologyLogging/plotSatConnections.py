from datetime import datetime
import sys
from io import StringIO
import pandas as pd
import re

f = open(sys.argv[1])
tops = f.read().split("\nEND TOPOLOGY\n")

times = []
cnts = []
for top in tops: 
    lines = top.split("\n")
    if (len(lines) < 3):
        continue
    time = lines[0]
    time = datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
    print(time)
    
    cnt = 0
    for line in lines[1:]:    
        if line == 'end of available map':
            break
        sat = int(line[:line.index(":")])
        
        trueGs = re.findall(',[^,]+?True', line)
        if len(trueGs) > 0:
            cnt += 1
    times.append(time)
    cnts.append(cnt)

import matplotlib.pyplot as plt
plt.plot_date(times, cnts)
plt.xlabel("Time")
plt.ylabel("Num of Satellites With More Than 2 Stations")
plt.savefig("satConnections.png")
