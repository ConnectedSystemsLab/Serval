#usage: python plotLatency.py [log.txt]
import matplotlib.pyplot as plt
import sys
import numpy as np
import overallLog

colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'w']
c = 0
plt.figure()

for fileName in sys.argv[1:]:
    latencys = []
    packetToTime = {}
    pacsAndLacs = []
    for row in overallLog.get_str(fileName, "Packet recieved by sat"):
        packetId = row['packetId']
        packetToTime[packetId] = row['time']
    
    timeToPacket = {}
    for row in overallLog.get_str(fileName, "Iot Recieved packet:"):
        receptionTime = row['time']
        
        if row['packetId'] in packetToTime.keys():
            lat = (receptionTime - packetToTime[row['packetId']]).total_seconds()
            latencys.append(lat)
            pacsAndLacs.append( (row['packetId'], lat) )
            del packetToTime[row['packetId']]

    pacsAndLacs.sort(key=lambda x: x[1])
    #or i in pacsAndLacs:
    #    print(i)
    print(fileName + " Total Packets:", len(latencys))
    
    num_bins = 100
    linewidth = 5
    counts, bin_edges = np.histogram (latencys, bins=num_bins, density=True)
    cdf = np.cumsum (counts)
    plt.plot (bin_edges[1:]/1000,cdf/cdf[-1],linewidth=linewidth,label=fileName, color=colors[c])
    c += 1

#make legend outside of plot on the top right
plt.legend(loc='upper left', bbox_to_anchor=(1, 1), ncol=1, fancybox=True, shadow=True)
plt.xlabel('Packet Latency',fontsize=18)
plt.ylabel('CDF',fontsize=18)
plt.title("Latency After Recieved By Sat")
#make the plot look nice
plt.tight_layout()
plt.savefig("plots/downlinkLatency.png")
