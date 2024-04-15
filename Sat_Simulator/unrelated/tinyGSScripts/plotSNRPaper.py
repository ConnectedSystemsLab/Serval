from typing import List
from datetime import datetime

import pandas as pd # type: ignore
import matplotlib.pyplot as plt # type: ignore
import numpy as np # type: ignore

from src.utils import Print, Time, Location
from src.satellite import Satellite
from src.station import Station
from src.routing import Routing
from src.links import Link

if __name__ == "__main__":
    #process flags etc
    #maybe check dependencies - I have skyfield 1.42
    #set up simulator class with info from config file
    ##code to do work on fullPacket.txt
    tle = ""
    groundStationLoc = (40.35476, -5.351)

    calculatedSNR = []
    theorySNR = []
    dates = []
    txt = pd.read_csv('SNR_data.csv')
    gsList = {}
    for id, row in txt.iterrows():
        date = datetime.utcfromtimestamp(row["gs_time"]/1000.0)
        currentTime = Time().from_datetime(date)

        lat, long = groundStationLoc

        gs = Station("", 0, Location().from_lat_long(lat, long))

        if row["fossaIdx"] == "FO012":
            sat = Satellite("FO012", "1 52773U 22057AT  23035.31275934  .00032402  00000-0  13901-2 0  9994\n2 52773  97.5324 153.4552 0009537  71.0628 289.1641 15.22618166 38582")
        elif row["fossaIdx"] == "FO008":
            sat = Satellite("FO008", "1 52779U 22057AZ  23035.25635710  .00035216  00000-0  16038-2 0  9995\n2 52779  97.5296 152.6288 0010499  77.9300 282.3111 15.20547380 38522")

        pos = sat.calculate_orbit(currentTime)
        dates.append(currentTime.datetime)
        
        snr = Link(sat, gs, currentTime).snr
        print(snr, row["SNR"])
        theorySNR.append(snr)
        calculatedSNR.append(row["SNR"])

    theory = np.array(theorySNR)
    exp = np.array(calculatedSNR)
    diff = theory - exp
    diff = np.nan_to_num(diff)

    print("diff average:", diff.std(), diff.mean())


    plt.plot_date(dates, theorySNR, label='theory')
    plt.plot_date(dates, calculatedSNR, label='expiremental')

    plt.xlabel("Time", fontsize=20)
    plt.ylabel("SNR (dB)", fontsize=20)
    
    plt.title("SNR of Passes")
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)
    plt.legend(fontsize=20)
    plt.savefig("SNR.png")
    