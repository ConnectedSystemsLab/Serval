import sys
import const

#const.ALPHA = float(sys.argv[1])
#const.LOGGING_FILE = "fixedLog"
const.ROUTING_MECHANISM = const.RoutingMechanism.assign_by_datarate_and_available_memory
const.ONLY_DOWNLINK = True
const.FIXED_SATELLITE_POSITION = True

from typing import List
from datetime import datetime
import random
import numpy as np

import pandas as pd # type: ignore
import matplotlib.pyplot as plt # type: ignore

from src.station import Station
from src.satellite import Satellite
from src.iotDevice import IotDevice
from src.recieveGS import RecieveGS
from src.utils import Print, Time, Location
from src.simulator import Simulator
from src.iotSatellite import IoTSatellite
from src.imageSatellite import ImageSatellite
from src.dataCenter import DataCenter

if __name__ == "__main__":
    #process flags etc
    #maybe check dependencies - I have skyfield 1.42
    #set up simulator class with info from config fil
    random.seed(101)
    np.random.seed(101)

    if __name__ == "__main__":
        stations = pd.read_json("referenceData/stations.json")
    
    groundStations: 'List[Station]' = []
    cnt = 0
    """
    for id, row in stations.iterrows():
        ##Randomly assign gs, make 1/4 recieve only, 3/4 transmit only
        num = random.random()
        s = Station(row["name"], id, Location().from_lat_long(row["location"][0], row["location"][1]))
        groundStations.append(RecieveGS(s))
        cnt += 1
    """
    latLst = [40] * 1
    lonLst = [-50] * 1
    altLst = [0] * 1
    #altLst[61] = 2000*1000-10
    
    locs = Location.multiple_from_lat_long(latLst, lonLst, altLst)
    
    iotCount = 0
    for loc in locs:
        gs = Station("IotDevice" + str(cnt), cnt, loc)
        cnt += 1
        #groundStations.append(IotDevice(gs, latLst[iotCount], lonLst[iotCount]))
        groundStations.append(RecieveGS(gs))
        iotCount += 1
    print("number of stations:" , len(stations))

    satellites = Satellite.load_from_tle("referenceData/swarm.txt")
    satellites = [ImageSatellite(i) for i in satellites]
    satellites = satellites[:1]
    satellites[0].position = Location().from_lat_long(40, -50, 2000*1000)
    #satellites[1].position = Location().from_lat_long(40, -50.1, 2000*1000)
    print("number of satellites:", len(satellites))
    
    dataCenter = Station("Data Center", -1, Location().from_lat_long(0, 0))
    dataCenter = DataCenter(dataCenter)

    startTime = Time().from_str("2022-07-15 12:00:00")
    endTime = Time().from_str("2022-07-15 12:02:00")

    sim = Simulator(60, startTime, endTime, satellites, groundStations)
    
    #sim.load_topology("top.txt") ##You can compute these topology maps once, save them, and load them instead of computing them every runtime
    #sim.calculate_topologys()  ##To precomute the topology maps. If they aren't precomuted, it will happen at runtime
    #sim.save_topology("top.txt") ##You can save these for any of the topologyLogging - take a look in the folder 
    sim.run()
    #sim.save_objects(".tmp") ## this will pickle and load all the objects until needed again