import sys
from datetime import datetime
import pickle

file = open(sys.argv[1], "r")
lines = file.readlines()
file.close()

lst = []
for line in lines:
    if "Timestep" in line or "Creating" in line:
        continue
    #year-month-day hour:minute:second datarate
    timeStr = line.split(" ")[0] + " " + line.split(" ")[1]
    datarate = float(line.split(" ")[2])
    time = datetime.strptime(timeStr, "%Y-%m-%d %H:%M:%S")
    lst.append((time, datarate))

pickle.dump(lst, open(sys.argv[2], "wb"))