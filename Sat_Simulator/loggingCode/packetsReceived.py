
##This compares the number packets lost to collisions compared to the number of packets created

import sys
import overallLog
import matplotlib.pyplot as plt

fileName = sys.argv[1]
tmpName = fileName.split(",")
p1 = float(tmpName[0].split("/")[1])
p2 = float(tmpName[1].split(".txt")[0])

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
    
for row in overallLog.get_str(fileName, "Iot Recieved packet:"):
    packetId = row['packetId']
    if packetId in packetsCreated:
        packetsRecieved[packetId] = True
    if packetId in packetsCollided.keys():
        packetsCollided.pop(packetId)


print("Packets created: " + str(len(packetsCreated)))
print("Packets collided: " + str(len(packetsCollided)))
print("Packets recieved: " + str(len(packetsRecieved)))
print("Packets Not Sent: " + str(len(packetsCreated) - len(packetsRecieved) - len(packetsCollided)))

##make pie chart
labels = ('Packets Not Sent', 'Packets Collided', 'Packets Recieved')
sizes = [len(packetsCreated) - len(packetsCollided) - len(packetsRecieved), len(packetsCollided), len(packetsRecieved)]

fig1, ax1 = plt.subplots()
ax1.pie(sizes, labels=labels, autopct='%1.1f%%')
ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
plt.title("P1: " + str(p1) + ", P2: " + str(p2) + ", total packets created: " + str(len(packetsCreated)))
plt.savefig("plots/" + str(p1) + "," + str(p2) + ".png")