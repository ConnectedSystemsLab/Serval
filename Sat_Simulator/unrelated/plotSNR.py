from typing import List
from datetime import datetime
import seaborn as sns
sns.set_theme()

import itur # type: ignore
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
    groundStationLoc = (40.42202, -3.70931)
    lat = 40.42202
    longNp = -3.70931

    calculatedSNR = []
    theorySNR = []
    dates = []
    txt = pd.read_csv('SNR_data.csv')
    gsList = {}
    gs = Station("gs", 0, Location().from_lat_long(groundStationLoc[0], groundStationLoc[1]))
    
    sat1 = Satellite("FO012", 52773, "1 52773U 22057AT  23035.31275934  .00032402  00000-0  13901-2 0  9994\n2 52773  97.5324 153.4552 0009537  71.0628 289.1641 15.22618166 38582")
    sat2 = Satellite("FO008", 52779, "1 52779U 22057AZ  23035.25635710  .00035216  00000-0  16038-2 0  9995\n2 52779  97.5296 152.6288 0010499  77.9300 282.3111 15.20547380 38522")
    sat3 = Satellite("FO011", 52750, "1 52750U 22057U   23035.31906786  .00045025  00000-0  18540-2 0  9994\n2 52750  97.5329 153.6102 0008387  70.2054 290.0086 15.23938351 38598")
    for id, row in txt.iterrows():
        #print(row["gs_time"]/1000)
        date = datetime.utcfromtimestamp(row["gs_time"]/1000.0)
        #convert the timezone from Spain to UTC (spain is 1 hour ahead)
        currentTime = Time().from_datetime(date)

        if row["fossaIdx"] == "FO012":
            sat = sat1
        elif row["fossaIdx"] == "FO008":
            continue
            sat = sat2
        elif row["fossaIdx"] == "FO011":
            continue
            sat = sat3

        print("Current time:", currentTime.to_str())
        pos = sat.calculate_orbit(currentTime)
        print("Satellite is at", pos.calculate_altitude_angle(gs.position), "degrees above horizon")
        dates.append(date)
        
        fsl = 20 * np.log10(distance) + 20 * np.log10(const.FREQUENCY) + 20 * np.log10(4 * np.pi / 3e8)

        alt = pos.calculate_altitude_angle(gs.position)

        A = itur.atmospheric_attenuation_slant_path(lat=lat, lon=longNp, f= 401.7e6/1e9, el=alt, p=0.00, D=1, R001=0, return_contributions=False)
        
        EIRP = -8
        BOTZMAN = 228.6 # in dB
        GR_T = -15.1 #Place holder for now
        LOG_BANDWIDTH = 10 * np.log10(const.BANDWIDTH)
        CONST = EIRP + BOTZMAN + GR_T - LOG_BANDWIDTH
        snrs = CONST - (fsl + A) + const.SNR_SCALING
        ##END of SNR model
        A = A.value
        print(snr, row["packet_snr"])
        theorySNR.append(snr)
        calculatedSNR.append(row["packet_snr"])

    theory = np.array(theorySNR)
    calculated = np.array(calculatedSNR)

    #split the data into a group for each time gap
    #find the time gaps
    timeGaps = []
    for i in range(len(dates)-1):
        timeGaps.append(dates[i+1] - dates[i])
    timeGaps = np.array(timeGaps)
    #find the time gaps that are greater than 1 hour
    timeGaps = np.where(timeGaps > np.timedelta64(1, 'h'))
    
    #split the data into groups
    theoryGroups = np.split(theory, timeGaps[0])
    calculatedGroups = np.split(calculated, timeGaps[0])
    timeGroups = np.split(dates, timeGaps[0])
    #remove all groups that have less than 10 data points
    theoryGroups = [x for x in theoryGroups if len(x) > 4]
    calculatedGroups = [x for x in calculatedGroups if len(x) > 4]
    timeGroups = [x for x in timeGroups if len(x) > 4]

    #create a new subplot for each group - the y axis is SNR and the x axis is time. There should be 1 row and however many columns are needed to fit all the subplots
    fig, axs = plt.subplots(1, len(theoryGroups), sharey=True, figsize=(20, 10), constrained_layout=True)
    fig.suptitle('SNR')
    for i in range(len(theoryGroups)):
        axs[i].scatter(timeGroups[i][1:-1], theoryGroups[i][1:-1], label="Theory", color="red")
        axs[i].scatter(timeGroups[i][1:-1], calculatedGroups[i][1:-1], label="Calculated", color="blue")
        #put only the start and end times on the x axis
        axs[i].set_xticks([timeGroups[i][1], timeGroups[i][-2]])
        axs[i].set_xticklabels([timeGroups[i][1].strftime("%Y-%m-%d %H:%M:%S"), timeGroups[i][-2].strftime("%Y-%m-%d %H:%M:%S")])
        #rotate the x axis labels
        for tick in axs[i].get_xticklabels():
            tick.set_rotation(45)

    axs[0].set_ylabel("SNR")
    axs[-1].legend()
    plt.tight_layout()
    plt.savefig("SNR.png")