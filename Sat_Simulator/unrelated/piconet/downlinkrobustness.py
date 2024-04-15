import subprocess
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import sys
import matplotlib
matplotlib.use("Agg")
def get_str(fileName, message):
    """
    This message will return a list of dictionaries for each row in the log file if the message matches the requested one
    """
    string = "grep -e '" + message + "' " + fileName
    result=subprocess.getoutput(string)
    txt = result.split('\n')
    times = {}

    outList = []
    cnt = 0

    for line in txt:
        cnt += 1
        lineDict = {}
        line = line.replace('\n', '')
        lineArr = line.split('\t')

        if lineArr == [''] or len(lineArr) == 0:
            continue

        mess = lineArr[1]

        if mess != message:
            continue

        timeStr = lineArr[0]
        if timeStr in times.keys():
            lineDict['time'] = times[timeStr]
        else:
            time = datetime.strptime(lineArr[0], "%Y-%m-%d %H:%M:%S")
            times[timeStr] = time
            lineDict['time'] = time

        basetime = datetime(2022,7,11,00,00,00)
        if time>basetime:
            break
        dupCount = 1
        for idx in range(2, len(lineArr)):
            elem = lineArr[idx]

            if '{' in elem and '}' in elem:
                elem = elem[1:-1]
                elem = elem.split(',')
                for pair in elem:
                    objs = pair.split(':')
                    key = objs[0].strip()
                    val = objs[1].strip()
                    
                    if key in lineDict.keys():
                        lineDict[key + str(dupCount)] = val
                        dupCount += 1
                    else:
                        lineDict[key] = val
            else:
                lineDict["idx" + str(idx)] = elem

        outList.append(lineDict)
    return outList


inputArgs = sys.argv

names = [inputArgs[1]]  
files = [inputArgs[2]]  



sns.set_theme()
fig, ax = plt.subplots()  #create figure and axes
fig.set_size_inches(5, 4)

for idx in range(len(names)):
    print(idx)
    value = get_str(files[idx],"Iot Recieved packet:")
    mapNode = {}
    print(value[0])
    for i in range(len(value)):
        keyv = value[i]["packetId"]
        mapNode[keyv] = mapNode.get(keyv, 0) + 1

    #print(type(np.array(mapNode.values())))
    packets = np.array([int(k) for k in mapNode.values()])

    print("Median",np.percentile(packets,50))
    print("90th",np.percentile(packets,90))
    counts, bin_edges = np.histogram(packets, bins=1000, density=True)
    cdf = np.cumsum(counts)
    if idx == 0:
        ls = 'solid'
        cl = "blue"
    elif idx == 1:
        ls = 'dotted'
        cl = "red"
    elif idx == 2:
        ls = 'dashed'
        cl = "green"
    ax.plot(bin_edges[1:],cdf/cdf[-1],linewidth=3,label=names[idx], linestyle = ls, color=cl)


ax.tick_params(axis='both', which='major',labelsize=18)
ax.legend(fontsize=18, loc='lower right')
ax.set_xlabel('# of GS Receiving Transmission',fontsize=18)
ax.set_ylabel('CDF',fontsize=18)
ax.set_xlim([0,20])
ax.set_xticks([1,2,4,6,8,10,12,14,16,18,20])
plt.tight_layout()
plt.savefig("downlinkrobustness.png")