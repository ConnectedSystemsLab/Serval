print("Starting")
import sys
import const

const.ONLY_UPLINK = False
const.ONLY_DOWNLINK = True
iotMax = 1000000
if const.ONLY_DOWNLINK:
    iotMax = 0

#ours = 14
#ours_and_l2d2 = 17
#single_and_l2d2 = 12
#aloha_and_l2d2 = 13
#single_and_ours = 15
#aloha_and_ours = 16

base = sys.argv[2]

if sys.argv[1] == "1":
    
    #const.INITIAL_ALPHA = float(sys.argv[3])
    #const.ALPHA_HIGHER_THRESHOLD = float(sys.argv[4])
    #const.ALPHA_DOWN_THRESHOLD = float(sys.argv[5])
    #const.ALPHA_INCREASE = float(sys.argv[6])
    #const.ROUTING_MECHANISM = const.RoutingMechanism.ours
    #the parameters are in the file called params.txt
    #sys.argv[3] is the line number of the file 
    line = open("params.txt").readlines()[int(sys.argv[3])]
    line = line.replace('\n', '')
    line = line.split(' ')
    const.INITIAL_ALPHA = float(line[0])
    const.ALPHA_HIGHER_THRESHOLD = float(line[1])
    const.ALPHA_DOWN_THRESHOLD = float(line[2])
    const.ALPHA_INCREASE = float(line[3])
    const.ROUTING_MECHANISM = const.RoutingMechanism.ours
    const.LOGGING_FILE = base + "ours-" + sys.argv[3] + ".log"
elif sys.argv[1] == "2":
    const.INITIAL_ALPHA = float(sys.argv[3])
    const.ALPHA_HIGHER_THRESHOLD = float(sys.argv[4])
    const.ALPHA_DOWN_THRESHOLD = float(sys.argv[5])
    const.ALPHA_INCREASE = float(sys.argv[6])
    const.ROUTING_MECHANISM = const.RoutingMechanism.ours_and_l2d2
    const.LOGGING_FILE = base + "ours_and_l2d2" + sys.argv[3] + "-" + sys.argv[4] + "-" + sys.argv[5] + "-" + sys.argv[6] + ".log"
elif sys.argv[1] == "3":
    const.ROUTING_MECHANISM = const.RoutingMechanism.single_and_l2d2
    const.LOGGING_FILE = base + "single_and_l2d2.log"
elif sys.argv[1] == "4":    
    const.ROUTING_MECHANISM = const.RoutingMechanism.aloha_and_l2d2
    const.LOGGING_FILE = base + "aloha_and_l2d2.log"
elif sys.argv[1] == "5":
    const.ROUTING_MECHANISM = const.RoutingMechanism.single_and_ours
    const.LOGGING_FILE = base + "single_and_ours.log"
elif sys.argv[1] == "6":
    const.ROUTING_MECHANISM = const.RoutingMechanism.aloha_and_ours
    const.LOGGING_FILE = base + "aloha_and_ours.log"
else:
    print("Invalid argument")
    exit()
print("Data Generation Rate", const.DATA_COLLECTION_FREQUENCY)
from typing import List
from datetime import datetime
import random

import pandas as pd # type: ignore
import matplotlib.pyplot as plt # type: ignore
import numpy as np # type: ignore

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

if __name__ == "__main__":
    print("Running")
    #process flags etc
    #maybe check dependencies - I have skyfield 1.42
    #set up simulator class with info from config fil
    random.seed(100)
    np.random.seed(100)
    groundStations: 'List[Station]' = []

    stations = pd.read_json("referenceData/stations.json")
    groundStations: 'List[Station]' = []
    cnt = 0
    
    for id, row in stations.iterrows():
        s = Station(row["name"], id, Location().from_lat_long(row["location"][0], row["location"][1]))
        groundStations.append(RecieveGS(s))
        cnt += 1
    
    print("Number of recieve:", cnt)
    if iotMax == 1000000:
        f = open("stationsLocsMillion.txt", "r")
        locs = f.readlines()
    elif iotMax == 100000:
        locs = open("piconet/stationsLocs100000.txt", "r").readlines()
    elif iotMax == 10000:
        locs = open("piconet/stationsLocs10000.txt", "r").readlines()
    else:
        #no iot devices
        locs = []

    latLst = []
    lonLst = []
    altLst = []
    for line in locs:
        line = line.replace('\n', '')
        line = line.split(',')
        latLst.append(float(line[0]))
        lonLst.append(float(line[1]))
        altLst.append(float(0))

    print("number of iot devices:", len(latLst))    

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
    startTime = Time().from_str("2022-07-09 00:00:00")
    endTime = Time().from_str("2022-07-10 00:00:00")
    
    sim = Simulator(60, startTime, endTime, satellites, groundStations)
    sim.run()