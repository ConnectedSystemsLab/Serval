import sys
import const

const.ONLY_UPLINK = False
const.ONLY_DOWNLINK = False
iotMax = 100

if sys.argv[1] == "1":
    const.INITIAL_ALPHA = float(sys.argv[2])
    const.ALPHA_HIGHER_THRESHOLD = float(sys.argv[3])
    const.ALPHA_DOWN_THRESHOLD = float(sys.argv[4])
    const.ALPHA_INCREASE = float(sys.argv[5])
    const.ROUTING_MECHANISM = const.RoutingMechanism.probability_with_hyperparameter
    const.LOGGING_FILE = "/home/ochabra2/logs/ours" + sys.argv[2] + "-" + sys.argv[3] + "-" + sys.argv[4] + "-" + sys.argv[5] + ".log"
elif sys.argv[1] == "2":
    const.ROUTING_MECHANISM = const.RoutingMechanism.transmission_probability_function
    const.LOGGING_FILE = "/home/ochabra2/logs/oneSat.log"
elif sys.argv[1] == "3":
    const.ROUTING_MECHANISM = const.RoutingMechanism.transmit_with_random_delay
    const.LOGGING_FILE = "/home/ochabra2/logs/aloha.log"
elif sys.argv[1] == "4":    
    const.ROUTING_MECHANISM = const.RoutingMechanism.l2d2
    const.LOGGING_FILE = "/home/ochabra2/logs/l2d2.log"
elif sys.argv[1] == "5":
    const.ROUTING_MECHANISM = const.RoutingMechanism.probability_with_hyperparameter
    const.LOGGING_FILE = "/home/ochabra2/logs/uplinkNoTune.log"
elif sys.argv[1] == "6":
    const.ROUTING_MECHANISM = const.RoutingMechanism.single_and_l2d2
    const.LOGGING_FILE = "/home/ochabra2/logs/singleAndL2d2.log"
elif sys.argv[1] == "7":
    const.ROUTING_MECHANISM = const.RoutingMechanism.aloha_and_l2d2
    const.LOGGING_FILE = "/home/ochabra2/logs/alohaAndL2d2.log"
else:
    print("Invalid argument")
    exit()

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
    #process flags etc
    #maybe check dependencies - I have skyfield 1.42
    #set up simulator class with info from config fil

    stations = pd.read_json("referenceData/stations.json")
    groundStations: 'List[Station]' = []
    cnt = 0
    
    for id, row in stations.iterrows():
        s = Station(row["name"], id, Location().from_lat_long(row["location"][0], row["location"][1]))
        groundStations.append(RecieveGS(s))
        cnt += 1
    
    print("Number of recieve:", cnt)
    print("Sanity")
    if iotMax == 1000000:
        print("1000000")
        locs = open("stationsLocsMillion.txt", "r").readlines()
    if iotMax == 100000:
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

    if len(locs) == 0:
        print("Generating random iot devices")
        latLst = list(np.random.uniform(-90, 90, iotMax))
        lonLst = list(np.random.uniform(-180, 180, iotMax))
        altLst = [0] * iotMax
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
    #sim.calculate_topologys()
    #sim.save_topology("tmp.txt")
    #sim.load_topology("/scratch/ochabra2/maps/2022-07-10-20:00:00.txt")
    sim.calcuate_and_save_topologys(iotMax)
    #sim.run()
