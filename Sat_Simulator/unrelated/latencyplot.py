import subprocess
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import sys 

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
                    if "generationTime" in pair:
                        splitray = pair.split(" ")
                        lineDict["generationTime"] = splitray[2] +" "+splitray[3]
                        continue
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

sns.set_theme()
fig, ax = plt.subplots()  #create figure and axes
fig.set_size_inches(5, 4)

inputArgs = sys.argv

if len(inputArgs) == 5:
    names = [inputArgs[1], inputArgs[2]]  
    files = [inputArgs[3], inputArgs[4]]  
else:
    names = [inputArgs[1], inputArgs[2], inputArgs[3]]  
    files = [inputArgs[4], inputArgs[5], inputArgs[6]] 

for idx in range(len(names)):
    value = get_str(files[idx],"Iot Recieved packet:")
    print(len(value))
    latency = []
    rgsmap = {}
    format: str = "%Y-%m-%d %H:%M:%S"

    packets = {}
    for i in range(len(value)):
        if value[i]['packetId'] not in packets.keys():
            packets[value[i]['packetId']] = True
            rgsmap[value[i]['packetId']] =  value[i]["time"]
    print("Packets",len(packets))
    rsatmap={}
    
    value = get_str(files[idx],"Packet recieved by sat")
    print(len(value))
    for i in range(len(value)):
        if value[i]['packetId'] in packets.keys() and value[i]['packetId'] not in rsatmap.keys():
            rsatmap[value[i]['packetId']] =  value[i]["time"]
    
    print("Packets",len(rsatmap))
    
    latency = []
    for key in rgsmap.keys():
        receivedongs = rgsmap[key]
        receiveonsat = rsatmap[key]
        latency.append((receivedongs-receiveonsat).total_seconds()/60.0)
    print("Number of packets",len(latency))

    print("Median",np.percentile(latency,50))
    print("90th",np.percentile(latency,90))
    counts, bin_edges = np.histogram(latency, bins=100, density=True)
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
    ax.plot(bin_edges[1:], cdf/cdf[-1],linewidth=3,label=names[idx], linestyle = ls, color =cl)

ax.tick_params(axis='both', which='major',labelsize=18)
ax.legend(fontsize=15, loc='lower right')
ax.set_xlabel('Freshness (min)',fontsize=15)
ax.set_ylabel('CDF',fontsize=15)
plt.tight_layout()
plt.savefig("latencycdf.png")