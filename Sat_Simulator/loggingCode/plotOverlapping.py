##usage: python plotWastedSlots.py logfile

import sys
from statistics import mean
import matplotlib.pyplot as plt
from datetime import datetime
import overallLog


times = []
slots = []
for row in overallLog.get_str(sys.argv[1], "GS in multiple"):
        times.append( row['time'] )
        slots.append( float(row['idx2']) )

fig = plt.figure()
plt.plot_date(times, slots)
plt.title("Number of Iot Devices That Are In Two Sats")
plt.legend()
fig.autofmt_xdate()
plt.savefig(sys.argv[1].replace('.txt', 'overlapping.png'))

