##usage: python plotWastedSlots.py logfile

import sys
from statistics import mean
import matplotlib.pyplot as plt
from datetime import datetime
import overallLog


times = []
slots = []
for row in overallLog.get_str(sys.argv[1], "Number of Free Slots"):
    if "SPACEBEE" in row["nodeName"]:
        times.append( row['time'] )
        slots.append( float(row['idx3']) )

fig = plt.figure()
plt.plot_date(times, slots)
plt.title("Number of Free Slots per Minute")
plt.legend()
fig.autofmt_xdate()
plt.savefig("plots/wasted.png")

