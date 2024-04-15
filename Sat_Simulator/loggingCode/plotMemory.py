##usage: python plotMemory.py logfile

import sys
from statistics import mean
import matplotlib.pyplot as plt
import overallLog

timesD = {}
for row in overallLog.get_str(sys.argv[1], 'Satellite Memory'):
    val = float(row['idx2'])
    time = row['time']

    if time not in timesD.keys():
        timesD[time] = [val]
    else:
        timesD[time].append(val)

maxs = []
avgs = []
mins = []
times = []
for key, val in timesD.items():
    times.append(key)
    avgs.append(mean(val))
    maxs.append(max(val))
    mins.append(min(val))

fig = plt.figure()
plt.plot_date(times, maxs, label="Max Memory In One Sat")
plt.plot_date(times, avgs, label="Average Memory In Whole Constellation")
plt.plot_date(times, mins, label="Min")
plt.ylabel("Percent of Memory Occupied")
plt.xlabel("Time")
plt.title("Overall Percent of Satellite Memory Occupied")
plt.legend()
fig.autofmt_xdate()
plt.savefig("plots/satmem.png")
