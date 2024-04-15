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
        #print(line)
        cnt += 1
        lineDict = {}
        line = line.replace('\n', '')
        lineArr = line.split('\t')

        if lineArr == [''] or len(lineArr) ==0:
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

        basetime = datetime(2022,7,10,00,00,00)
        if time>basetime:
            break
        dupCount = 1
        for idx in range(2, len(lineArr)):
            elem = lineArr[idx]

            if '{' in elem and '}' in elem:
                elem = elem[1:-1]
                elem = elem.split(',')
                for pair in elem:
                    if "generationTime" in pair:
                        splitray = pair.split(" ")
                        lineDict["generationTime"] = splitray[2] +" "+splitray[3]
                        continue
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

def round_five(x):
    return 5 * round(x/5)

inputArgs = sys.argv

if len(inputArgs) == 5:
    names = [inputArgs[1], inputArgs[2]]  
    files = [inputArgs[3], inputArgs[4]]  
else:
    names = [inputArgs[1], inputArgs[2], inputArgs[3]]  
    files = [inputArgs[4], inputArgs[5], inputArgs[6]]  

sns.set_theme()
fig, ax = plt.subplots()  #create figure and axes
fig.set_size_inches(5,4)

#desiredLat = -37.84
#desiredLon = 145.00
desiredLat = 41.85
desiredLon = -87.85
inArea = {}

plt.xlim([datetime(2022,7,9,00,00,00), datetime(2022,7,11,0,00,00)])
for idx in range(len(names)):
    print(idx)

    #Let's get the list 
    if len(inArea) == 0:
        locs = get_str(files[idx],"Node Created")
        for i in range(len(locs)):
            if "Iot" in locs[i]["nodeName"]:
                keyt = locs[i]["nodeId"]
                lat = float(locs[i]["idx3"])
                lon = float(locs[i]["idx4"])
                #if within 1 degree of desired lat and lon
                if abs(lat-desiredLat) < 3 and abs(lon-desiredLon) < 3:
                    print(keyt, lat, lon)
                    inArea[keyt] = 1

    timeToCount = {}
    value = get_str(files[idx],"Iot Recieved packet:")
    #First get list of throughputs for each nodes
    for i in range(len(value)):
        if value[i]["nodeId"][:-1] in inArea.keys():
            time = value[i]["generationTime"]
            time = datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
            if time in timeToCount.keys():
                timeToCount[time] += 1
            else:
                timeToCount[time] = 1

    #now let's plot the throughput over time
    x = []
    y = []
    for key in timeToCount.keys():
        x.append(key)
        y.append(timeToCount[key])
    
    x = np.array(x)
    y = np.array(y)

    if idx == 0:
        ls = 'solid'
        cl = "blue"
    elif idx == 1:
        ls = 'dotted'
        cl = "red"
    elif idx == 2:
        ls = 'dashed'
        cl = "green"
    plt.plot_date(x, y, label=names[idx], linestyle=ls, color=cl, marker='None', linewidth=1.5)
    ###ONWARDS
    
#draw a vertical line at "2022-07-9 20:00:00" and "2022-07-10 4:00:00"
#2022-07-10 12:00:00"), Time().from_str("2022-07-10 18:00:00
plt.axvline(x=datetime(2022,7,10,12,00,00), color='k', linestyle='--', linewidth=1.5)
plt.axvline(x=datetime(2022,7,10,18,00,00), color='k', linestyle='--', linewidth=1.5)

plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("fairness.png")