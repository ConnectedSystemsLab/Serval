import os
import shelve
from typing import Dict, List, Optional, no_type_check, TYPE_CHECKING
import sys
import math
from time import time as time_now
from collections import Iterable
from typing import Dict, List
from collections.abc import Iterable

from matplotlib import pyplot as plt

from src.utils import Time, Print
from src.routing import Routing
from src.satellite import Satellite
from src.station import Station
from src.links import Link
from src.data import Data
from src.packet import Packet
from src.topology import Topology
from src.node import Node
from src.transmission import Transmission
from src.groundTransmission import GroundTransmission
from src.dataCenter import DataCenter
from src import log

import const

class Simulator:
    """
    Main class that runs simulator

    Attributes:
        timestep (float/seconds) - timestep in seconds. CURRENTLY MUST BE AN INTEGER NUMBER
        startTime (Time) - Time object to when to start
        endTime (Time) - Time object for when to end (simulation will end on this timestep. i.e if end time is 12:00 and timeStep is 10, last run will be 11:59:50)
        satList (List[Satellite]) - List of Satellite objects
        gsList (List[Station]) - List of Station objects
        topologys (Dict[str, Topology]) - dictionary of time strings to Topology objects
        recreated (bool) - wether or not this simulation was recreated from saved file. If true, then don't compute for t-1 timestep
    """
    def __init__(self, timeStep: float, startTime: Time, endTime: Time, satList: 'List[Satellite]', gsList: 'List[Station]', recreated: bool = False) -> None:

        self.timeStep = timeStep
        self.startTime = startTime
        self.endTime = endTime
        self.satList = satList
        self.gsList = gsList
        self.recreated = recreated
        self.topologys: 'Dict[str, Topology]' = {}
        #log.clear_logging_file()
    
    def calcuate_and_save_topologys(self, n) -> None:
        if not os.path.exists(const.MAPS_PATH):
            os.makedirs(const.MAPS_PATH)
        time = self.startTime.copy()
        print("End of stations")
        while time < self.endTime:
            print("Map for time: ", time)
            file = const.MAPS_PATH + time.to_str().replace(" ", "-") + ".pkl"
            if os.path.exists(file):
                print("File already exists")
                time.add_seconds(self.timeStep)
                continue
            t = Topology(time, self.satList, self.gsList)
            f = open(file, "wb+")
            t.save(f)
            f.close()
            time.add_seconds(self.timeStep)
        f.close()
        
    def live_plot(self) -> None:
        #Let's try to plot the data live
        print("Plotting live")
        
        satelliteImg = "imgs/satellite.png"
        groundImg = "imgs/3770310.png"
        iotImg = "imgs/iotdevnb.png"

        gd = Geodesic()
        plt.rcParams['font.size'] = 20
        plt.rcParams["font.monospace"] = ["DejaVu Sans Mono"]
        plt.rcParams["font.family"] = "monospace"
        #if threeDimensions:
        map = ccrs.Orthographic(-10, 45)
            #map = ccrs.PlateCarree()
        #else:
        #    map = ccrs.PlateCarree()
        transform = ccrs.PlateCarree()

        print("Creating figure1")
        fig = plt.figure(figsize=(3, 3))
        print("Creating figure2")
        ax = fig.add_subplot(projection=map)
        print("Creating figure3")
        #ax.coastlines()
        #ax.stock_img()
        ax.set_global()
        #ax.gridlines()
        ax.add_feature(cartopy.feature.OCEAN, facecolor='#F2F2F2')
        ax.add_feature(cartopy.feature.LAND, facecolor='#A6A6A6')
        geoms = []

        iotDevices = [i for i in self.gsList if i.transmitAble]
        iotLat = [i.lat for i in iotDevices]
        iotLon = [i.lon for i in iotDevices]

        gsDevices = [i for i in self.gsList if not i.transmitAble]
        stationLocs = [i.position for i in gsDevices]
        stationLat, stationLon, altList = Location.multiple_to_lat_long(stationLocs)

        print("Adding ground stations")
        for i in range(len(stationLat)):
            ab = AnnotationBbox(OffsetImage(plt.imread(groundImg), zoom=0.01), (stationLon[i], stationLat[i]), frameon=False, xycoords=transform._as_mpl_transform(ax), pad=0.0)
            ax.add_artist(ab)

        for i in range(len(iotLat)):
            print("Adding iot")
            ab = AnnotationBbox(OffsetImage(plt.imread(iotImg), zoom=0.01), (iotLon[i], iotLat[i]), frameon=False, xycoords=transform._as_mpl_transform(ax), pad=0.0)
            ax.add_artist(ab)
        
        plt.show(block=False)

    def calculate_topologys(self) -> None:
        """
        Use this to calculate all the topologys. Can be saved to file using save_topology

        Returns:
            None - will load topology into self.topologys
        """
        time = self.startTime.copy()
        while time < self.endTime:
            Print("Map for time: ", time)
            t = Topology(time, self.satList, self.gsList)
            print(t.save())
            #self.topologys[time.to_str()] = Topology(time, self.satList, self.gsList)
            time.add_seconds(self.timeStep)
        Print(self.topologys)


    def save_topology(self, filename: str) -> None:
        """
        This method will save all the topology objects to a file. Can be loaded using load_topology
        Arguments:
            filename (str) - filename to save to. Will be w+ (overwrite)
        """
        with open(filename, "w+") as f:
            for key, val in self.topologys.items():
                f.write(val.save() + "\nEND TOPOLOGY\n")

            f.close()

    def load_topology(self, filename: str) -> None:
        """
        Load topology from file. This will be run after the simulation is created and before the simulation is run

        Arguments:
            filename (str) - filename to load from
        Returns:
            None - will load topology into self.topologys
        """
        with open(filename, "r") as f:
            top = Topology.load(f, self.satList, self.gsList)
            f.close()
            print(top)
        return top

    def run(self) -> None:
        """
        At inital, load one time step of data into object
        then schedule based off of new data
        send info
        """
        time = self.startTime.copy()
        log.update_logging_time(time)

        log.Log("Routing algorithm", const.ROUTING_MECHANISM)
        iotDevices = [i for i in self.gsList if i.transmitAble]
        nIot = len(iotDevices)
        
        ##Start sim:
        while time < self.endTime:
            s = time_now()
            #print("Simulation at", time.to_str())
            log.update_logging_time(time)

            #if the topology maps have been created - this should load from storage and not re-compute anything
            for sat in self.satList:
                sat.calculate_orbit(time)

            #Calculate data for timeStep
            for sat in self.satList:
                sat.load_data(self.timeStep)
                sat.load_packet_buffer()
            
            for gs in self.gsList:
                gs.load_data(self.timeStep)
                gs.load_packet_buffer()
            
            if const.INCLUDE_UNIVERSAL_DATA_CENTER:
                DataCenter.universalDataCenter.load_data(self.timeStep)
                DataCenter.universalDataCenter.load_packet_buffer()

            if const.INCLUDE_POWER_CALCULATIONS:
                for sat in self.satList:
                    sat.generate_power(self.timeStep)
                    log.Log("Satellite power", sat.maxMWs, sat.currentMWs, sat)
                    sat.use_regular_power(self.timeStep)

            filePath = const.MAPS_PATH + time.to_str().replace(" ", "-") + ".pkl"
            if not const.ONLY_DOWNLINK and os.path.exists(filePath):
                try:
                    print("Loading maps from", filePath)
                    topology = Topology.load(filePath, self.satList, self.gsList)
                except Exception as e:
                    print(e)
                    print("Error loading map, recreating maps")
                    topology = Topology(time, self.satList, self.gsList)
            else:
                print("Creating maps")
                topology = Topology(time, self.satList, self.gsList)

            routing = Routing(topology, self.timeStep)
            links = routing.bestLinks # Dict[Satellite][Station] = Link

            Transmission(links, topology, self.satList, self.gsList, self.timeStep)

            if const.INCLUDE_UNIVERSAL_DATA_CENTER:
                GroundTransmission(self.gsList, self.timeStep)

            self.logAtTimestep()

            time.add_seconds(self.timeStep)
            print("Timestep took", time_now() - s)
            
        log.close_logging_file()
            

    def logAtTimestep(self):
        for sat in self.satList:
           log.Log("Satellite Memory", sat.percent_of_memory_filled(), sat, len(sat.transmitPacketQueue), len(sat.recievePacketQueue))

        for gs in self.gsList:
           log.Log("Iot Memory", len(gs.transmitPacketQueue), gs)

        log.update_logging_file()

    def save_objects(self, fileName: str) -> None:
        """
        Will save all the variables in this class and logging to the specified file

        Arguments:
            fileName (str)
        """
        variables = vars(self)
        shelf = shelve.open(fileName, 'n')
        test_shelf = shelve.open(".tst") #to test if objects can be shelved, if not, they are thrown out

        ##for each variable and its value, in the elements
        for var, val in variables.items():
            if var != "routes":

                ##if list, process it before saving
                if isinstance(val, Iterable):

                    ##loop through each object
                    for elementInList in val:

                        ##if the object is any user defined type, we have to check that it is saveable
                        if type(elementInList) != str:

                            ##test if every individual object can be saved
                            for elemVar, elemVel in vars(elementInList).items():

                                ##if the object is not saveable, we have to throw it out
                                try:
                                    test_shelf[var + "." + str(elementInList)] = elemVel
                                except:
                                    ##normally throw it out, however, nodeDecorator objects still have _node objects that need to be saved
                                    if isinstance(elemVel, Node):
                                        ##check if deleting skyfield will fix this
                                        if isinstance(elemVel, Satellite):
                                            elemVel.delete_skyfield()
                                    else:
                                        ##if we can't save it, we have to throw it out
                                        setattr(elementInList, elemVar, None)
                                        Print("Could not save", var + "." + str(elementInList) + "and it's value " + str(elemVar))


                #save the object itself
                shelf[var] = val

        ##do this manually cause not in class
        shelf["logCurrentTime"] = log.loggingCurrentTime
        shelf["logLoggingString"] = log.loggingString
        shelf["logLoggingObjs"] = log.loggingObjs
        shelf["logTimes"] = log.loggingTimes
        shelf["dataCounter"] = Data.idCount
        shelf["packetCounter"] = Packet.idCount

        shelf.close()
        del test_shelf

    @staticmethod
    @no_type_check ##Ignore type checking for this cause objects are being loaded from stored
    def open_stored_simulator(fileName: str, timeStepNew: 'Optional[float]' = None, startTimeNew: 'Optional[Time]' = None, endTimeNew: 'Optional[Time]'  = None) -> 'Simulator':
        """
        Opens stored stimulator in the given file.

        Arguments:
            fileName (str) - file to open
            timeStepNew (float) - new time step in seconds, by default None to set to original timestep
            startTimeNew (Time) - new start time as Time object, by default None to set to original startTime
            endTimeNew (Time) - new end time as Time object, by default None to set to original endTime
        Returns:
            Simulator - returns a new simulator object with new routes based on inputed times. Call run on this object to start simulation
        """
        ##pdoc is the tool to create the documentation, this method crashes it, so I'm disabling it
        if not 'pdoc' in sys.modules:
            my_shelf = shelve.open(fileName)

            for key in my_shelf:
                Print("Loading from Memory:", key)
                globals()[key]=my_shelf[key] ##These really should be local but for some reason this wouldn't work with locals()
            my_shelf.close()

            [i.setup_skyfield() for i in satList] ##issue with skyfield not being able to be pickled

            log.loggingCurrentTime = logCurrentTime.copy()
            log.loggingString = logLoggingString
            log.loggingObjs = logLoggingObjs
            log.loggingTimes = logTimes

            Data.idCount = dataCounter
            Packet.idCount = packetCounter

            ##These really should be local but for some reason this wouldn't work with locals()
            global timeStep
            global startTime
            global endTime

            if timeStepNew:
                timeStep = timeStepNew
            if startTimeNew:
                startTime = startTimeNew
            if endTimeNew:
                endTime = endTimeNew

            return Simulator(timeStep, startTime, endTime, satList, gsList, True)

        else:
            pass


