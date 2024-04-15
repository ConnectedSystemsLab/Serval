
##This compares the number packets lost to collisions compared to the number of packets created

import sys
import overallLog
import matplotlib.pyplot as plt

fileName = sys.argv[1]
f = open(fileName, "r")
lines = f.readlines()
lines = lines[4:]
f.close()

lines = [int(i[:-1].split(":")[1]) for i in lines]

cnt = {}

for i in lines:
    if i not in cnt:
        cnt[i] = 0
    cnt[i] += 1


#make pie chart
labels = list(cnt.keys())
sizes = list(cnt.values())

fig1, ax1 = plt.subplots()
ax1.pie(sizes, labels=labels, autopct='%1.1f%%')
ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
plt.title("Num of Satellites Seen While Transmitting (baseline) 100 sats/10,000 Iots")
plt.savefig("plots/satPie.png")
