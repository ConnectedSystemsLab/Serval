from datetime import datetime
import sys
from io import StringIO
import pandas as pd
import re

f = open(sys.argv[1])
tops = f.read().split("\nEND TOPOLOGY\n")


devicesToTime = {}
gsAndTimeToCount = {}
for top in tops: 
    lines = top.split("\n")
    if (len(lines) < 3):
        continue
    time = lines[0]
    time = datetime.strptime(time, "%Y-%m-%d %H:%M:%S")

    for line in lines[1:]:
        trueGs = re.findall('(\d+)\sTrue', line)
        for gs in trueGs:
            id = int(gs)
            if id in devicesToTime:
                devicesToTime[id].append(time)
            else:
                devicesToTime[id] = [time]
            
            if (id, time) in gsAndTimeToCount:
                gsAndTimeToCount[(id, time)] += 1
            else:
                gsAndTimeToCount[(id, time)] = 1


#make a plot for each device
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

#make a plot for all devices
fig, ax = plt.subplots(nrows=len(devicesToTime))
i = 0
for id, times in devicesToTime.items():
    ax[i].plot_date(times, [gsAndTimeToCount[(id, time)] for time in times])
    ax[i].xaxis.set_major_formatter(mdates.DateFormatter('%d'))
    i += 1

plt.xlabel("Day in Simulation")
plt.ylabel("Numbers of Sats in View")
plt.savefig("allDevices.png")
