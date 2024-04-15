
FREQUENCY = 401.7e6
BANDWIDTH = 125e3 

import scipy
import numpy as np
import itur
from matplotlib import pyplot as plt
import pandas as pd
import json
import seaborn as sns
sns.set_theme()

gs = pd.read_json('referenceData/stations.json')

def calcuate_model(distance, elev, lat=0, long=0):
#https://www.kymetacorp.com/wp-content/uploads/2020/09/Link-Budget-Calculations-2.pdf
    fsl = 20 * np.log10(distance) + 20 * np.log10(FREQUENCY) + 20 * np.log10(4 * np.pi / 3e8)
    return 8 -fsl
    #A = itur.atmospheric_attenuation_slant_path(lat=lat, long=long, f= FREQUENCY/1e9, el=elev, p=0.01, D=1, R001=0, return_contributions=False)
    A = 0

    EIRP = -8
    #BOTZMAN = 228.6 # in dB
    BOTZMAN = 0
    GR_T = -15.1 #Place holder for now
    LOG_BANDWIDTH = 10 * np.log10(BANDWIDTH)
    CONST = EIRP + BOTZMAN + GR_T - LOG_BANDWIDTH
    snrs = CONST - (fsl + A) + -20 
    return snrs

data = pd.read_csv('tinyGsData.csv')
print(data.keys())
data = data[data['crc'] == 0]

theory = []
val = []

for id, row in data.iterrows():
    snr = calcuate_model(1000*row['distance_km'], row['elevation'])
    theory.append(snr)
    val.append(row['rssi'])
    print(id, snr, row['rssi'])

theory = np.array(theory)
val = np.array(val)
diff = np.array(theory) - np.array(val)
#remove outliers (more than 3 std away from the mean)
#diff = diff[np.abs(diff - np.mean(diff)) < 3 * np.std(diff)]
#diffInds = np.argwhere(np.abs(diff - np.mean(diff)) < 2 * np.std(diff))
diffInds = np.arange(len(diff))
diff = diff[diffInds]
print("Mean:", np.mean(diff), "Std:", np.std(diff))

theory = theory[diffInds]
val = val[diffInds]

#let's bin theory every 1 dB and plot the mean and std of the real world values
bins = np.arange(min(theory), max(theory), .5)
inds = np.digitize(theory, bins)
means = []
stds = []
for i in range(1, len(bins)):
    means.append(np.median(val[inds == i]))
    stds.append(scipy.stats.iqr(val[inds == i])/2)

plt.figure(figsize=(7,7))
#let's do a histogram where x axis is theory and y axis is real world values. Let's draw the mean and an error bar for the std
lines = plt.errorbar(bins[2:], means[1:], yerr=stds[1:], fmt='o', label='Real World', color='blue', ecolor='lightgreen', elinewidth=3, capsize=0)
#set the y axis to be the same as the x axis
plt.plot([min(bins), max(bins)], [min(bins), max(bins)], label='Theory = Real World')
#make the ticks on the x and y axis the same
plt.gca().set_aspect('equal', adjustable='box')
plt.xlim([min(bins), max(bins)])
plt.ylim([min(bins), max(bins)])

#find the r squared value for the y=x line

plt.legend()
plt.tick_params(axis='both', which='major',labelsize=25)
#make a tick on the x axis every 2 dB
plt.xticks(np.arange(-145, -130, 4))
plt.yticks(np.arange(-145, -130, 4))
plt.xticks(rotation=45)
plt.legend(fontsize=18, loc='upper left')
plt.xlabel('Link Model (dBm)',fontsize=25)
plt.ylabel('Real-World RSSI (dBm)',fontsize=25)
plt.tight_layout()
plt.savefig('linkModel.png')

