import sys
import const

#const.ALPHA = float(sys.argv[1])
#const.LOGGING_FILE = "fixedLog"
print(const.ALPHA)
print(const.LOGGING_FILE)
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

from mpl_toolkits.basemap import Basemap # type: ignore

if __name__ == "__main__":
    #process flags etc
    #maybe check dependencies - I have skyfield 1.42
    #set up simulator class with info from config fil

    
    stations = pd.read_json("referenceData/stations.json")
    groundStations: 'List[Station]' = []
    latLst = [row["location"][0] for id, row in stations.iterrows()]
    lonLst = [row["location"][1] for id, row in stations.iterrows()]
    
    latLst = latLst[::50]
    lonLst = lonLst[::50]
    
    #latLst = [40, 40, 40, 40, 40]
    #lonLst = [-130, -129, -131, -124, -126]
    #altLst = [0, 0, 0, 0, 0]
    #iotCount = 3

    """
    locs = Location.multiple_from_lat_long(latLst, lonLst, altLst)

    iotCount = 0
    for loc in locs:
        iotCount += 1
        cnt += 1
        gs = Station("IoT" + str(iotCount), cnt, loc)
        groundStations.append(IotDevice(gs))

    Station.plot_stations(groundStations, True, "groundstations.png")
    """
    map = Basemap(projection='merc')
    #map.fillcontinents(color='grey',lake_color='white')
    #map.drawcoastlines()
    latList = []
    lonList = []
    altList = []

    iotCount = 0
    iotMax = 13
    while len(latList) < iotMax:
        #gererate random lat and lon all over the world
        lat = random.uniform(-90, 90)
        lon = random.uniform(-180, 180)
        print(lat, lon)
        x, y = map(lon, lat)
        if map.is_land(x,y):
            latList.append(lat)
            lonList.append(lon)
    #Add last two IoT devices
    latList.append(31.7464)
    lonList.append(10.3408)
    latList.append(16.865)
    lonList.append(-8.61004)

    print("number of stations:" , len(groundStations))
    
    satellites: 'List[Satellite]' = Satellite.load_from_tle("referenceData/updatedFossa")
    satellites = [IoTSatellite(i) for i in satellites]
    startTime = Time().from_str("2023-01-25 01:33:39")
    [i.calculate_orbit(startTime) for i in satellites]
    print("number of satellites:", len(satellites))
    latLst=[]
    LonLst=[]
    latList=[]
    lonList=[]
    Satellite.plot_satellites(satellites, latLst, lonLst, latList, lonList, True, "ofigure.png")
