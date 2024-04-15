from datetime import datetime
import subprocess

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

        mess = lineArr[1].strip()
        mess=mess.replace(':','').strip()

        if mess != message:
            continue

        timeStr = lineArr[0]
        if timeStr in times.keys():
            lineDict['time'] = times[timeStr]
        else:
            time = datetime.strptime(lineArr[0], "%Y-%m-%d %H:%M:%S")
            times[timeStr] = time
            lineDict['time'] = time


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

def get_str_with_callback(fileName, message, callback):
    string = "grep -e '" + message + "' " + fileName
    
    times = {}

    outList = []
    cnt = 0

    p = subprocess.Popen(string, stdout=subprocess.PIPE, shell=True, bufsize=1)
    for line in iter(p.stdout.readline, b''):
        line = line.decode('utf-8')
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

        callback(lineDict)
    
