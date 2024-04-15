import sys
import const
import os

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
from src.iotSatellite import IoTSatellite
from src.routing import Routing
from src.links import Link
from src.simulator import Simulator
from src.iotSatellite import IoTSatellite

if __name__ == "__main__":
    #process flags etc
    #maybe check dependencies - I have skyfield 1.42
    #set up simulator class with info from config fil
    random.seed(100)
    np.random.seed(100)
    stations = pd.read_json("referenceData/stations.json")
    groundStations: 'List[Station]' = []
    cnt = 0
    for id, row in stations.iterrows():
        if 25 < row["location"][0] < 45 and 0 < row["location"][1] < 20: 
            s = Station(row["name"], id, Location().from_lat_long(row["location"][0], row["location"][1]))
            groundStations.append(RecieveGS(s))
            cnt += 1
    groundStations = groundStations[::7]
    iotCount = 0
    latLst = [40.35476,36.1597,40.42202, 40.42202]
    lonLst = [-5.351, -3.74397, -3.70931,-3.70931]
    altLst = [0,0,0,0]
    
    locs = Location.multiple_from_lat_long(latLst, lonLst, altLst)

    """
    iotCount = 0
    for loc in locs:
        iotCount += 1
        cnt += 1
        gs = Station("IoT" + str(iotCount), cnt, loc)
        groundStations.append(IotDevice(gs, latLst[iotCount-1], lonLst[iotCount-1]))
    """
    print("number of stations:" , len(groundStations))

    satellites: 'List[Satellite]' = Satellite.load_from_tle("referenceData/updatedFossa") #specificSat for debugging
    satellites = [IoTSatellite(i) for i in satellites]
    #Satellite.plot_satellites(satellites, True, "satellites.png")
    print("number of satellites:", len(satellites))
    
    #startTime = Time().from_str("2023-02-8 12:00:00")
    #endTime = Time().from_str("2023-02-13 00:00:00")
    startTime = Time().from_str("2023-02-9 01:14:00")
    endTime = Time().from_str("2023-02-9 01:16:10")
    [i.calculate_orbit(startTime) for i in satellites]
    print(satellites[0].position.to_lat_long())
    
    sim = Simulator(60, startTime, endTime, satellites, groundStations)
    #sim.calcuate_and_save_topologys()
    #sim.calculate_topologys()
    sim.run()

    #sim.save_topology("top.txt")
