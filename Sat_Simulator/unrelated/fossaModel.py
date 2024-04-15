
FREQUENCY = 401.7e6
BANDWIDTH = 125e3 

import numpy as np
import itur
from matplotlib import pyplot as plt
import pandas as pd
import json
from src.satellite import Satellite
from src.station import Station
from src.utils import Location, Time
from datetime import datetime

gs = pd.read_json('referenceData/stations.json')

def calcuate_model(distance, elev, lat=0, long=0):
#https://www.kymetacorp.com/wp-content/uploads/2020/09/Link-Budget-Calculations-2.pdf
    fsl = 20 * np.log10(distance) + 20 * np.log10(FREQUENCY) + 20 * np.log10(4 * np.pi / 3e8)

    #A = itur.atmospheric_attenuation_slant_path(lat=lat, long=long, f= FREQUENCY/1e9, el=elev, p=0.01, D=1, R001=0, return_contributions=False)
    A = 0

    EIRP = -8
    BOTZMAN = 228.6 # in dB
    GR_T = -15.1 #Place holder for now
    LOG_BANDWIDTH = 10 * np.log10(BANDWIDTH)
    CONST = EIRP + BOTZMAN + GR_T - LOG_BANDWIDTH
    snrs = CONST - (fsl + A) + -20 
    return snrs

theory = []
val = []

data = pd.read_csv('SNR_data.csv')
#sat1 = Satellite("FO012", 52773, "1 52773U 22057AT  23035.31275934  .00032402  00000-0  13901-2 0  9994\n2 52773  97.5324 153.4552 0009537  71.0628 289.1641 15.22618166 38582")
sat1 = Satellite("FO008", 52750, "1 52750U 22057U   23035.31906786  .00045025  00000-0  18540-2 0  9994\n2 52750  97.5329 153.6102 0008387  70.2054 290.0086 15.23938351 38598")
gs = Station("Gs1", 1, Location().from_lat_long(40.42202, -3.70931))

for id, row in data.iterrows():
    if row['fossaIdx'] != 'FO008':
        continue
    sat1.calculate_orbit(Time().from_datetime(datetime.utcfromtimestamp(row["gs_time"]/1000)))
    dist = sat1.position.get_distance(gs.position)
    snr = calcuate_model(dist, sat1.position.calculate_altitude_angle(gs.position))
    theory.append(snr)
    val.append(row['packet_snr'])
    print(id, snr, row['packet_snr'])

plt.figure()
plt.plot(theory, val, 'o')
#plot the line y=x
plt.plot([min(theory), max(theory)], [min(theory), max(theory)], 'k', lw=4)
plt.xlabel('Theory')
plt.ylabel('Val')
plt.title('Theory vs Val SNR')
plt.savefig("linkModel.png")

