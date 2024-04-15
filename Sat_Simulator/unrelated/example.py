print("Starting to import everyting")
from typing import List
import pandas as pd #type: ignore
import random

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
print("Starting to run code")
if __name__ == "__main__":
    stations = pd.read_json("referenceData/stations.json")

    groundStations: 'List[Station]' = []
    cnt = 0
    for id, row in stations.iterrows():
        ##Randomly assign gs, make 1/4 recieve only, 3/4 transmit only
        num = random.random()
        s = Station(row["name"], id, Location().from_lat_long(row["location"][0], row["location"][1]))
        if num < .25:
            groundStations.append(RecieveGS(s))
        else:
            cnt += 1
            groundStations.append(IotDevice(s))

    print("number of stations:" , len(stations))

    satellites = Satellite.load_from_tle("referenceData/swarm.txt")
    satellites = [IoTSatellite(i) for i in satellites]
    print("number of satellites:", len(satellites))

    startTime = Time().from_str("2022-07-15 12:00:00")
    endTime = Time().from_str("2022-07-15 13:00:00")

    sim = Simulator(60, startTime, endTime, satellites, groundStations)
    
    #sim.load_topology("top.txt") ##You can compute these topology maps once, save them, and load them instead of computing them every runtime
    #sim.calculate_topologys()  ##To precomute the topology maps. If they aren't precomuted, it will happen at runtime
    #sim.save_topology("top.txt") ##You can save these for any of the topologyLogging - take a look in the folder 
    sim.run()
    #sim.save_objects(".tmp") ## this will pickle and load all the objects until needed again