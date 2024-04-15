#let's put one million lat, lon pairs in a file
#make a list of 10^6 lat, lon pairs and write them to stationsLocsMillion.txt

import numpy as np

lat = np.random.uniform(-90, 90, 1000000)
lon = np.random.uniform(-180, 180, 1000000)

f = open("stationsLocsMillion.txt", "w+")
for i in range(len(lat)):
    f.write(str(lat[i]) + "," + str(lon[i]) + "\n")
f.close()