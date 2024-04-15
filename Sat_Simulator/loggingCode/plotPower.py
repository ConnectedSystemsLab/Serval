##usage: python plotMemory.py logfile

import sys
from statistics import mean
import matplotlib.pyplot as plt
import overallLog

timesD = {}
for row in overallLog.get_str(sys.argv[1], 'Satellite power'):
    val = float(row['idx3'])/3600
    print(val)
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
plt.plot_date(times, maxs, label="Max Power In One Sat")
plt.plot_date(times, avgs, label="Average Power In Whole Constellation")
plt.plot_date(times, mins, label="Mininim Power In One Sat")
plt.ylabel("Power Available (mWh)")
plt.xlabel("Time")
plt.title("Overall Power Capacity")
plt.legend()
fig.autofmt_xdate()
plt.savefig("plots/satpower.png")
