##run this from the directory of the logs
#python3 ../loggingCode/slotsWithMultipleProbability.py *.log
import sys
import overallLog
import matplotlib.pyplot as plt
import numpy as np

p1s = []
p2s = []
vals = []
#sort fileNames by probability - they are in the format of "p1,p2.txt"
#first sort by p1, then by p2
fileNames = sys.argv[1:]
fileNames.sort(key=lambda x: float(x.split(",")[0]))
fileNames.sort(key=lambda x: float(x.split(",")[1].split(".txt")[0]))
print(fileNames)

for fileName in fileNames:
    print(fileName)
    p1 = float(fileName.split(",")[0])
    p2 = float(fileName.split(",")[1].split(".txt")[0])

    p1s.append(p1)
    p2s.append(p2)

    satValues = {}
    for row in overallLog.get_str(fileName, "Number of Successful Slots"):
        satValues[row["nodeName"]] = float(row["idx3"])
    
    #take the average of the number of successful slots for each satellite
    avgSuccessfulSlots = sum(satValues.values()) / len(satValues)
    print("Average successful slots: " + str(avgSuccessfulSlots))
    vals.append(avgSuccessfulSlots)

"""
uniqueP1s = list(set(p1s))
fig = plt.figure()
for p1 in uniqueP1s:
    ##make a new plot for each p1
    ##the x axis will be p2
    ##the y axis will be the percentage of packets collided, recieved, and not sent
    p2sForP1 = []
    valsForP1 = []
    for i in range(len(p1s)):
        if p1s[i] == p1:
            p2sForP1.append(float(p2s[i]))
            valsForP1.append(float(vals[i]))

    print("P1: " + str(p1) + ", p2s: " + str(p2sForP1) + ", slots: " + str(valsForP1))
    ##make the plot

    plt.plot(p2sForP1, valsForP1, label=float(p1))

plt.title("Packets Recieved")
plt.xlabel("p2")
plt.ylabel("Percentage of packets")
plt.xticks(np.arange(0.05, .25, .05))
#plt.set_xscale('log')
plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
#plt.set_ylim([0,1])
"""
#make a heatmap
#x axis is p1
#y axis is p2
#z axis is the number of successful slots
#make a 2d array of the values

uniqueP1s = list(set(p1s))
uniqueP2s = list(set(p2s))
uniqueP1s.sort()
uniqueP2s.sort()

#make a 2d array of the values
vals2d = []
for p1 in uniqueP1s:
    valsForP1 = []
    for p2 in uniqueP2s:
        for i in range(len(p1s)):
            if p1s[i] == p1 and p2s[i] == p2:
                valsForP1.append(vals[i])
    vals2d.append(valsForP1)

print(vals2d)

plt.imshow(vals2d, cmap='hot', interpolation='nearest')
plt.title("Number of Successful Slots")
plt.xlabel("p1")
plt.ylabel("p2")
plt.xticks(np.arange(0, len(uniqueP1s), 1), uniqueP1s)
plt.yticks(np.arange(0, len(uniqueP2s), 1), uniqueP2s)
plt.colorbar()

plt.tight_layout()
plt.savefig("slots.png")

