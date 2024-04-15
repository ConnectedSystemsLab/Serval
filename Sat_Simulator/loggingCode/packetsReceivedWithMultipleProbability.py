##run this from the directory of the logs
#python3 ../loggingCode/packetsReceivedWithMultipleProbability.py *.log
##This compares the number packets lost to collisions compared to the number of packets created

import sys
import overallLog
import matplotlib.pyplot as plt
import numpy as np

p1s = []
p2s = []
packetsCollidedPercentage = []
packetsRecievedPercentage = []
packetsNotSentPercentage = []

#sort fileNames by probability - they are in the format of "p1,p2.txt"
#first sort by p1, then by p2
fileNames = sys.argv[1:]
print(fileNames)
for fileName in fileNames:
    print(fileName)
    p1 = float(fileName.split(",")[0])
    p2 = float(fileName.split(",")[1].split(".txt")[0])
    packetsCreated = {}
    packetsCollided = {}
    packetsRecieved = {}

    for row in overallLog.get_str(fileName, "Packet Created by "):
        if "ack" not in row['packetDescriptor']:
            packetId = row['packetId']
            packetsCreated[packetId] = True

    for row in overallLog.get_str(fileName, "Packets in collision:"):
        for key, val in row.items():
            if "packetId" in key:
                ##first check if the packet was created from a data object and not an ack
                if val in packetsCreated and val not in packetsCollided and val not in packetsRecieved:
                    packetsCollided[val] = True
        
    for row in overallLog.get_str(fileName, "Packet recieved by sat"):
        packetId = row['packetId']
        if packetId in packetsCreated:
            packetsRecieved[packetId] = True
        if packetId in packetsCollided.keys():
            packetsCollided.pop(packetId)

    #remove packets from packetsCreated that were not sent
    i = 0
    #while i < len(packetsCreated):
    #    packetId = list(packetsCreated.keys())[i]
    #    if packetId not in packetsCollided and packetId not in packetsRecieved:
    #        packetsCreated.pop(packetId)
    #    else:
    #        i += 1
    print("Packets created: " + str(len(packetsCreated)))
    print("Packets collided: " + str(len(packetsCollided)))
    print("Packets recieved: " + str(len(packetsRecieved)))
    print("Packets Not Sent: " + str(len(packetsCreated) - len(packetsRecieved) - len(packetsCollided)))

    ##make pie chart
    #labels = ('Packets Not Sent', 'Packets Collided', 'Packets Recieved')
    #sizes = [len(packetsCreated) - len(packetsCollided) - len(packetsRecieved), len(packetsCollided), len(packetsRecieved)]

    #fig1, ax1 = plt.subplots()
    #ax1.pie(sizes, labels=labels, autopct='%1.1f%%')
    #ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    #plt.title("P1: " + str(p1) + ", P2: " + str(p2) + ", total packets created: " + str(len(packetsCreated)))
    #plt.savefig("plots/" + str(p1) + "," + str(p2) + ".png")

    p1s.append(p1)
    p2s.append(p2)
    packetsCollidedPercentage.append(len(packetsCollided))
    packetsRecievedPercentage.append(len(packetsRecieved))
    packetsNotSentPercentage.append((len(packetsCreated) - len(packetsRecieved) - len(packetsCollided)))

##make a new stacked bar chart for each p1
uniqueP1s = list(set(p1s))
fig, axes = plt.subplots(2)
for p1 in uniqueP1s:
    ##make a new plot for each p1
    ##the x axis will be p2
    ##the y axis will be the percentage of packets collided, recieved, and not sent
    p2sForP1 = []
    packetsCollidedPercentageForP1 = []
    packetsRecievedPercentageForP1 = []
    packetsNotSentPercentageForP1 = []
    for i in range(len(p1s)):
        if p1s[i] == p1:
            p2sForP1.append(float(p2s[i]))
            packetsCollidedPercentageForP1.append(packetsCollidedPercentage[i])
            packetsRecievedPercentageForP1.append(packetsRecievedPercentage[i])
            packetsNotSentPercentageForP1.append(packetsNotSentPercentage[i])
    
    print("P1: " + str(p1) + ", p2s: " + str(p2sForP1) + ", packets collided: " + str(packetsCollidedPercentageForP1) + ", packets recieved: " + str(packetsRecievedPercentageForP1) + ", packets not sent: " + str(packetsNotSentPercentageForP1))
    ##make the plot
    """
    plt.bar(p2sForP1, packetsCollidedPercentageForP1, width=.35, color='r')
    plt.bar(p2sForP1, packetsNotSentPercentageForP1, width=.35, bottom=packetsCollidedPercentageForP1, color='b')
    plt.bar(p2sForP1, packetsRecievedPercentageForP1, width=.35, bottom= [i+j for i,j in zip(packetsCollidedPercentageForP1, packetsNotSentPercentageForP1)], color='g')
    plt.title("P1: " + str(p1))
    plt.xlabel("P2")
    plt.ylabel("Percentage of packets")
    plt.legend(["Packets Collided", "Packets Not Sent", "Packets Received"], loc='center left', bbox_to_anchor=(1, 0.5))
    plt.tight_layout()
    plt.savefig("plots/" + str(p1) + ".png")
    plt.clf()
    """
    #add a line to the plot
    #0 is the percentage of packets collided
    #1 is the percentage of packets recieved

    axes[0].plot(p2sForP1, packetsCollidedPercentageForP1, label=p1)
    axes[1].plot(p2sForP1, packetsRecievedPercentageForP1, label=p1)

axes[0].set_title("Packets Collided")
axes[0].set_xlabel("P2")
axes[0].set_ylabel("Percentage of packets")
#axes[0].set_xscale('log')
axes[0].legend(loc='center left', bbox_to_anchor=(1, 0.5))
#x label every .05
axes[0].set_xticks(np.arange(0.05, .25, .05))
#axes[0].set_ylim([0,1])

axes[1].set_title("Packets Recieved")
axes[1].set_xlabel("P2")
axes[1].set_ylabel("Percentage of packets")
axes[1].set_xticks(np.arange(0.05, .25, .05))
#axes[1].set_xscale('log')
axes[1].legend(loc='center left', bbox_to_anchor=(1, 0.5))
#axes[1].set_ylim([0,1])

plt.tight_layout()
plt.savefig("packetDestinations.png")

