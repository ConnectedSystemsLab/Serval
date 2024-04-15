import sys
import const

from typing import List
from datetime import datetime
import random

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
import src.log as log

if __name__ == "__main__":
    satellites: 'List[Satellite]' = Satellite.load_from_tle("referenceData/updatedFossa")
    satellites = [IoTSatellite(i) for i in satellites]
    print("number of satellites:", len(satellites))
    startTime = Time().from_str("2022-05-08 12:00:00")
    endTime = Time().from_str("2022-05-10 00:00:00")

    sim = Simulator(60, startTime, endTime, satellites, [])
    #sim.calculate_topologys()
    sim.run()
    #sim.save_topology("tmp.txt")
    #sim.calcuate_and_save_topologys()
