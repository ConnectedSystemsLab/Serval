
import math
import random
import numpy as np
from time import time as timeNow
from src.data import Data
from src.packet import Packet
from src.log import Log
from shapely.geometry import Point, Polygon
from src.utils import Time
from src.log import get_logging_time

import const

from src.nodeDecorator import NodeDecorator


desiredTimes = [(Time().from_str("2022-07-10 12:00:00"), Time().from_str("2022-07-10 18:00:00")), (Time().from_str("2022-07-10 18:00:00"), Time().from_str("2022-07-11 2:00:00")), (Time().from_str("2022-07-10 20:00:00"), Time().from_str("2022-07-11 04:00:00")), (Time().from_str("2022-07-10 20:00:00"), Time().from_str("2022-07-11 04:00:00")),(Time().from_str("2022-07-11 20:00:00"), Time().from_str("2022-07-12 4:00:00")), (Time().from_str("2022-07-9 20:00:00"), Time().from_str("2022-07-10 4:00:00")), (Time().from_str("2022-07-14 15:00:00"), Time().from_str("2022-07-14 21:00:00")), (Time().from_str("2022-07-13 01:00:00"), Time().from_str("2022-07-13 07:00:00")),(Time().from_str("2022-07-12 5:00:00"), Time().from_str("2022-07-12 11:00:00")), (Time().from_str("2022-07-12 17:00:00"), Time().from_str("2022-07-12 23:00:00"))]
latLongs = [(41.85, -87.85), (19.42, -99.09), (-34.59, -58.52), (25.18, 55.22), (40.71, -73.95), (-37.84, 145.00), (35.74, 139.63), (41.87, 12.47), (-26.23, 28.05), (78.98, -8.09)]

class IotDevice(NodeDecorator):
    """
    Decorator object for a node object, normally used on a station object.
    It will make it so that the node object can only transmit, and not recieve.
    """
    def __init__(self, node: 'Node', lat, lon) -> None:
        """
        Station class but transmit only.
        """
        super().__init__(node)
        ##self._node is a station object, so set transmit only
        self.transmitAble = True
        self.recieveAble = False
        self.beamForming = False
        self.groundTransmitAble = False
        self.groundReceiveAble = False
        self.lat = lat
        self.lon = lon
        self.alpha = const.INITIAL_ALPHA
        self.waitForAck = False
        #make a polygon of arizona
    
    def in_event(self):
        for i in range(len(latLongs)):
            #if within 1 degree of the desired location, then it is in the desired location
            if abs(self.lat - latLongs[i][0]) < 1 and abs(self.lon - latLongs[i][1]) < 1 and desiredTimes[i][0] < get_logging_time() < desiredTimes[i][1]:
                self.inPoint = True
                return True

    def recieve_packet(self, pck: 'Packet') -> None:
        """
        Code to recieve packet and add it to packet buffer

        Arguments:
            pck (Packet) - packet recieved
        """
        #Do nothing cause transmit only!
        return
        
        #self.packetQueue.appendleft(pck)
        #print("Recieved packet:", pck)
        if "ack" in pck.descriptor:
            self.recieve_ack(pck)
        else:
            self.generate_ack(pck)
        pass

    def load_data(self, timeStep: float, numData) -> None:
        """
        For Iot GS, creates 30 bits over one hour
        """
        if const.ONLY_DOWNLINK:
            return
        #if self.lat and self.lon are in the desired location, and the time is in the desired time, then the data_collection_frequency is 1/3 of the normal value
        #if self.in_event():
        #    numData = np.random.binomial(timeStep, 1/(const.DATA_COLLECTION_FREQUENCY / 4))
        numData = round(numData)
        if numData > 0:
            dataObjects = [Data(const.DATA_SIZE, relevantNode=self, generationTime=get_logging_time()) for i in range(numData)]
            #dataObjects = [Data(const.DATA_SIZE) for i in range(numData)]
            #Log("Data Created By", self, *dataObjects)
            self.dataQueue.extendleft(dataObjects)
        
    def load_packet_buffer(self) -> None:
        """
        Adds a packet to the packet buffer
        """
        if const.ONLY_DOWNLINK:
            return
        self.convert_data_objects_to_transmit_buffer()

    def increase_alpha(self):
        self.alpha = self.alpha + const.ALPHA_INCREASE
        #Log("Alpha", self, self.alpha)

    def decrease_alpha(self):
        self.alpha = self.alpha/2
        #Log("Alpha", self, self.alpha)
        
