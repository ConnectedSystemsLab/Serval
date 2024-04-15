import const
import numpy as np
import pandas as pd
import random
import sys

from src.station import Station
from src.satellite import Satellite
from src.iotDevice import IotDevice
from src.recieveGS import RecieveGS
from src.utils import Print, Time, Location
from src.iotSatellite import IoTSatellite
from src.routing import Routing
from src.links import Link
from src.simulator import Simulator
from src.iotSatellite import IoTSatellite
import src.log as log

iotMax = 1000000

if __name__ == "__main__":
    random.seed(100)
    np.random.seed(100)
    
    stations = pd.read_json("referenceData/stations.json")
    groundStations: 'List[Station]' = []
    cnt = 0
    
    for id, row in stations.iterrows():
        s = Station(row["name"], id, Location().from_lat_long(row["location"][0], row["location"][1]))
        groundStations.append(RecieveGS(s))
        cnt += 1
    
    print("Number of recieve:", cnt)
    print("Maps for iot devices:", iotMax)
    if iotMax == 1000000:
        f = open("stationsLocsMillion.txt", "r")
        locs = f.readlines()
    elif iotMax == 100000:
        print("100000")
        locs = open("stationsLocs100000.txt", "r").readlines()
    elif iotMax == 10000:
        print("10000")
        locs = open("stationsLocs10000.txt", "r").readlines()
    else:
        #no iot devices
        locs = []
    
    print("number of iot devices:", len(locs))
    latLst = []
    lonLst = []
    altLst = []
    for line in locs:
        line = line.replace('\n', '')
        line = line.split(',')
        latLst.append(float(line[0]))
        lonLst.append(float(line[1]))
        altLst.append(float(0))
        
    locs = Location.multiple_from_lat_long(latLst, lonLst, altLst)
    
    iotCount = 0
    for loc in locs:
        gs = Station("IotDevice" + str(cnt), cnt, loc)
        cnt += 1
        groundStations.append(IotDevice(gs, latLst[iotCount], lonLst[iotCount]))
        iotCount += 1
        
    print("number of stations:" , len(groundStations))

    satellites: 'List[Satellite]' = Satellite.load_from_tle("referenceData/swarm.txt")
    satellites = [IoTSatellite(i) for i in satellites]
    print("number of satellites:", len(satellites))
    
    time = sys.argv[1]
    time = int(time) # time is an integer from 1 to 96
    #split the 24 hours into 96 15 minute intervals
    startTime = Time().from_str("2022-07-09 00:00:00")
    startTime.add_seconds((time - 1) * 15 * 60)
    endTime = startTime.copy()
    endTime.add_seconds(15 * 60)
    
    print("start time:", startTime)
    print("end time:", endTime)
    
    sim = Simulator(60, startTime, endTime, satellites, groundStations)
    sim.calcuate_and_save_topologys(iotMax)