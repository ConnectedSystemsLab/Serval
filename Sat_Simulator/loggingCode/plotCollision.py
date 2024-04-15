import matplotlib.pyplot as plt
import sys
import overallLog

packetToTime = {}

fig = plt.figure()

for file in sys.argv[1:]:
    for row in overallLog.get_str(file, 'Packets in collision:'):
        for key, val in row.items():
            if 'packetId' in key and not val in packetToTime.keys():
                packetToTime[int(val)] = row['time']

    ##reverse the dictionary
    timeToPacketCount = {}
    for key, val in packetToTime.items():
        if val in timeToPacketCount:
            timeToPacketCount[val] += 1
        else:
            timeToPacketCount[val] = 1

    #make this cumulative
    for i in range(1, len(timeToPacketCount)):
        timeToPacketCount[list(timeToPacketCount.keys())[i]] += timeToPacketCount[list(timeToPacketCount.keys())[i-1]]
        
    plt.plot_date(timeToPacketCount.keys(), timeToPacketCount.values(), label=file)
    plt.legend()
plt.title("Collisions in The Whole System Every Time Step")
plt.xlabel("Time")
plt.ylabel("Number of Collisions")
fig.autofmt_xdate()
plt.savefig("plots/collisions1.png")
