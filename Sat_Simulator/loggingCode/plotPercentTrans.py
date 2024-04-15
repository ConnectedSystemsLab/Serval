#usage: python plotLatency.py [log.txt]
import matplotlib.pyplot as plt
import sys
import numpy as np
import overallLog

fileName = sys.argv[1]

dataToPackets = {}
packetsToData = {}
dataToTime = {}
dataToNode = {}

timeToObjects = {}
timeToCount = {}

for row in overallLog.get_str(fileName, "Data Created By"):
    time = row["time"]
    dataToTime[row['dataId']] = time

    if time in timeToObjects.keys():
        timeToObjects[time].append(row['dataId'])
        timeToCount[time] += 1
    else:
        timeToObjects[time] = [row['dataId']]
        timeToCount[time] = 1

for row in overallLog.get_str(fileName, "Packet Created by "):
    packetId = row['packetId']
    dataId = row['dataId']

    packetsToData[packetId] = dataId
    dataToPackets[packetId] = packetId

for row in overallLog.get_str(fileName, "Iot Recieved packet:"):
    packetId = row['packetId']
    dataId = packetsToData[packetId]
    creationTime = dataToTime[dataId]

    if dataId in timeToObjects[creationTime]:
        timeToObjects[creationTime].remove(dataId)

outTimes = []
outPercents = []

for time in timeToCount.keys():
    outPercents.append( 1 - len(timeToObjects[time])/timeToCount[time] )
    outTimes.append(time)

fig = plt.figure()
plt.title("Overall Throughput Of Simulation")
plt.plot_date(outTimes, outPercents)
plt.xlabel("Data Creation Time")
plt.ylabel("Percent Recieved At End Of Simulation")
fig.autofmt_xdate()
plt.savefig("plots/percent.png")