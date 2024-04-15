
##This compares the number packets lost to collisions compared to the number of packets created

import sys
import overallLog
import matplotlib.pyplot as plt

fig = plt.figure()
alphaToCollisions = {}
for fileName in sys.argv[1:]:
    print(fileName)
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
                if val in packetsCreated:
                    packetsCollided[val] = True
        
    for row in overallLog.get_str(fileName, "Packet recieved by sat"):
        packetId = row['packetId']
        if packetId in packetsCreated:
            packetsRecieved[packetId] = True
        if packetId in packetsCollided.keys():
            packetsCollided.pop(packetId)

    print("Alpha: " + str(fileName))
    print("Packets created: " + str(len(packetsCreated)))
    print("Packets collided: " + str(len(packetsCollided)))
    print("Packets recieved: " + str(len(packetsRecieved)))
    print("Packets Not Sent: " + str(len(packetsCreated) - len(packetsRecieved) - len(packetsCollided)))
    print("Ratio of collided: ", str(len(packetsCollided)/len(packetsCreated)))
    print("Ratio of Recieved", str(len(packetsRecieved)/len(packetsCreated)))