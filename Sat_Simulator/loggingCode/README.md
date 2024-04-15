Here is where all the logging scripts are, feel free to add your own, but here's what we have so far
 - makeAll.py - runs all of the plotting code in the folder
 - overallLog.py - functionality that all the other loggers use
 - plotCollision.py - plots the number of packet collisions at each timestep
 - plotDownlink.py - plots the downlink latency for each packet as a CDF
 - plotIotMemory.py - plots the memory capacity of the iotDevices
 - plotLatency.py - plots the latency of all of the data objects from creation to reception
 - plotMemory.py - plots the memory usage of the satellites
 - plotOverlapping.py - plots the number of devices that are in two sats at one time
 - plotPercentTrans.py - plots the percent of data objects that are received at each timeStep by the end of the simulation
 - plotPower.py - plots the energy usage of the satellites
 - plotWastedSlots.py - plots the number of available transmission slots (where 1 is a const.MICRO_TIMESTEP frame) 

To run all of these run python [script] [loggingFile] - i.e. python makeAll.py log.txt

