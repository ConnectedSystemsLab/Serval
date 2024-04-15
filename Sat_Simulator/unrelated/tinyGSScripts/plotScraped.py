from typing import List
from datetime import datetime

import pandas as pd # type: ignore
import matplotlib.pyplot as plt # type: ignore
import numpy as np # type: ignore

from utils import Print, Time, Location
from satellite import Satellite
from station import Station
from routing import Routing
from links import Link

if __name__ == "__main__":
    #process flags etc
    #maybe check dependencies - I have skyfield 1.42
    #set up simulator class with info from config file
    ##code to do work on fullPacket.txt

    stations = pd.read_json("TinyGS_Data/stations.json")
    groundStations = {}
    for id, row in stations.iterrows():
            groundStations[row["name"]] = (row["location"][0], row["location"][1])

    calculatedSNR = []
    theorySNR = []
    dates = []
    txt = pd.read_csv('TinyGS_Data/scrapedP.txt')
    gsName =  "PE1MEW"
    satName = "Norby"
    satTle = "1 46494U 20068J   22157.57763368  .00002710  00000-0  19533-3 0  9999\n2 46494  97.7295  99.0517 0016818 324.8294  35.1819 15.04918509 92566" #norby tuesday
    #satTle = "1 51001U 22002T   22158.42504501  .00012213  00000-0  59923-3 0  9992\n2 51001  97.4897 226.2336 0014613 100.6550 259.6330 15.18152148 21938" #fossa 2e5
    for id, row in txt.iterrows():
        if satName in row["Sat"]:
            currentTime = Time().from_str(row[" Time"])

            lat, long = groundStations[gsName]

            gs = Station(gsName, 0, Location().from_lat_long(lat, long))
            sat = Satellite("", 46494, satTle)
            sat.position = sat.caculate_orbit(currentTime)
            
            dates.append(currentTime.to_datetime())
            
            snr = Link(sat, gs, currentTime).snr
            print(snr, row[" SNR"])
            theorySNR.append(snr)
            calculatedSNR.append(row[" SNR"])

    theory = np.array(theorySNR)
    exp = np.array(calculatedSNR)
    diff = theory - exp
    diff = np.nan_to_num(diff)

    print("diff average:", diff.std(), diff.mean())


    plt.plot_date(dates, theorySNR, label='theory')
    plt.plot_date(dates, calculatedSNR, label='expiremental')

    plt.xlabel("Time", fontsize=20)
    plt.ylabel("SNR (dB)", fontsize=20)
    
    plt.title("SNR of Multiple Passes between PE1MEW and Norby Without Scaling", fontsize=20)
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)
    plt.legend(fontsize=20)
    plt.show()
