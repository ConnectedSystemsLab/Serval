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

for idx in range(len(names)):
    print(idx)
    value = get_str(files[idx],"Alpha")
    mapNode = {}
    #First get list of throughputs for each nodes
    mapNode = {}
    print(value[0])
    for i in range(len(value)):
            keyv = value[i]["nodeId"][:-1]
            mapNode[keyv] = mapNode.get(keyv, 0) + 1

    #Next get the list 
    mapLat = {}
    lats = get_str(files[idx],"Node Created")
    for i in range(len(lats)):
        if "Iot" in lats[i]["nodeName"]:
            keyt = lats[i]["nodeId"]
            mapLat[keyt] = float(lats[i]["idx3"])



    for key in mapLat.keys():
        # make a list out of the string
        mapLat[key] = round_five(mapLat[key])

    final_dict = {i: [] for i in range(-90, 91, 5)}

    for key in mapNode.keys():
        latcor = mapLat[key]
        tp = mapNode[key]
        final_dict[latcor].append(tp)

    mean_dict = {}
    std_dict = {}

    for key in final_dict.keys():
        mean_dict[key] = np.array(final_dict[key]).mean()
        std_dict[key] = np.array(final_dict[key]).std()
    ax.scatter(mean_dict.keys(),mean_dict.values(),label = names[idx])
    ax.errorbar(mean_dict.keys(),mean_dict.values(),yerr = np.array([float(k) for k in std_dict.values()]))

ax.tick_params(axis='both', which='major',labelsize=18)
ax.legend(fontsize=18, loc='lower right')
ax.set_xlabel('Latitude',fontsize=18)
ax.set_ylabel('Throughput',fontsize=18)
plt.tight_layout()
plt.savefig("fairness.png")