#usage: python plotLatency.py [log.txt]
import matplotlib.pyplot as plt
import sys
import numpy as np
import overallLog

colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'w']
c = 0
plt.figure()

#list = []
for fileName in sys.argv[1:]:
    packet = {}
    timeToPacketCount = {}
    for row in overallLog.get_str(fileName, "Iot Recieved packet:"):
        if 'packetId' not in row.keys():
            print(row)
            continue
        receptionTime = row['time']
        if row['packetId'] not in packet.keys():
            if receptionTime in timeToPacketCount.keys():
                timeToPacketCount[receptionTime] += 1
            else:
                print("new time:", receptionTime)
                timeToPacketCount[receptionTime] = 1
            packet[row['packetId']] = receptionTime

    #plt.plot_date(list(timeToPacketCount.keys()), list(timeToPacketCount.values()), '.', label=fileName, color=colors[c])
    #plot cdf of number of packets received
    x = list(timeToPacketCount.keys())
    x.sort()
    sums = np.cumsum([timeToPacketCount[k] for k in x])
    plt.plot_date(x, sums, '.', label=fileName, color=colors[c])
    c += 1
    #print the slope of the line:
    firstTime = x[0]
    firstSum = sums[0]
    lastTime = x[-1]
    lastSum = sums[-1]
    slope = (lastSum - firstSum) / (lastTime - firstTime).total_seconds()
    print("Number of packets received per second:", slope)
    #list.append(timeToPacketCount)

#list should have two dictionaries, find the difference
#x = list[0].keys()
#diff = [list[0][k] - list[1][k] for k in x]
#plt.plot_date(x, diff, '.', label="Greedy - set", color=colors[0])
#make legend outside of plot on the top right
plt.legend(loc='upper left', bbox_to_anchor=(1, 1), ncol=1, fancybox=True, shadow=True)
#make the x axis labels readable - rotate them
plt.gcf().autofmt_xdate()

plt.xlabel('Time Received at GS',fontsize=18)
#plt.ylabel('Cummulative Count',fontsize=18)
plt.ylabel("Number of Packets Received", fontsize=18)
plt.title("Downlink Throughput")
#make the plot look nice
plt.tight_layout()
plt.savefig("plots/downlinkThroughput.png")
